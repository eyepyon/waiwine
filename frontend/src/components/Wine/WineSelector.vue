<template>
  <div class="wine-selector">
    <div class="search-section">
      <h3>{{ $t('wine.manual_selection') }}</h3>
      
      <!-- Search input -->
      <div class="search-input-container">
        <input
          v-model="searchQuery"
          @input="onSearchInput"
          :placeholder="$t('wine.search_placeholder')"
          class="search-input"
          type="text"
        />
        
        <div class="search-icon">🔍</div>
      </div>
      
      <!-- Filters -->
      <div class="filters" v-if="showFilters">
        <div class="filter-row">
          <select v-model="filters.wine_type" @change="performSearch" class="filter-select">
            <option value="">{{ $t('wine.all_types') }}</option>
            <option v-for="type in wineTypes" :key="type.value" :value="type.value">
              {{ type.label }}
            </option>
          </select>
          
          <select v-model="filters.region" @change="performSearch" class="filter-select">
            <option value="">{{ $t('wine.all_regions') }}</option>
            <option v-for="region in wineRegions" :key="region.value" :value="region.value">
              {{ region.label }} ({{ region.wine_count }})
            </option>
          </select>
          
          <input
            v-model="filters.vintage"
            @input="performSearch"
            :placeholder="$t('wine.vintage')"
            class="filter-input"
            type="number"
            min="1800"
            max="2030"
          />
        </div>
        
        <button @click="clearFilters" class="clear-filters-btn">
          {{ $t('common.clear_filters') }}
        </button>
      </div>
      
      <button @click="toggleFilters" class="toggle-filters-btn">
        {{ showFilters ? $t('common.hide_filters') : $t('common.show_filters') }}
      </button>
    </div>
    
    <!-- Loading state -->
    <div v-if="loading" class="loading-state">
      <div class="loading-spinner"></div>
      <div>{{ $t('common.loading') }}</div>
    </div>
    
    <!-- Search results -->
    <div v-else-if="searchResults.length > 0" class="search-results">
      <h4>{{ $t('wine.search_results') }} ({{ searchResults.length }})</h4>
      
      <div class="wine-list">
        <div
          v-for="wine in searchResults"
          :key="wine.id"
          @click="selectWine(wine)"
          class="wine-item"
          :class="{ 'selected': selectedWine?.id === wine.id }"
        >
          <div class="wine-image">
            <img v-if="wine.image_url" :src="wine.image_url" :alt="wine.name" />
            <div v-else class="wine-placeholder">🍷</div>
          </div>
          
          <div class="wine-info">
            <div class="wine-name">{{ wine.name }}</div>
            <div class="wine-details">
              <span v-if="wine.producer" class="producer">{{ wine.producer }}</span>
              <span v-if="wine.vintage" class="vintage">{{ wine.vintage }}</span>
              <span v-if="wine.region" class="region">{{ wine.region }}</span>
            </div>
            <div v-if="wine.wine_type_label" class="wine-type">{{ wine.wine_type_label }}</div>
            <div v-if="wine.recognition_count > 0" class="popularity">
              👥 {{ wine.recognition_count }} {{ $t('wine.recognitions') }}
            </div>
          </div>
          
          <div class="select-indicator">
            <div v-if="selectedWine?.id === wine.id" class="selected-icon">✓</div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- No results -->
    <div v-else-if="searchQuery && !loading" class="no-results">
      <div class="no-results-icon">🔍</div>
      <div class="no-results-text">{{ $t('wine.no_results') }}</div>
      <div class="no-results-suggestion">{{ $t('wine.try_different_search') }}</div>
    </div>
    
    <!-- Popular wines (when no search) -->
    <div v-else-if="!searchQuery && popularWines.length > 0" class="popular-wines">
      <h4>{{ $t('wine.popular_wines') }}</h4>
      
      <div class="wine-list">
        <div
          v-for="wine in popularWines"
          :key="wine.id"
          @click="selectWine(wine)"
          class="wine-item"
          :class="{ 'selected': selectedWine?.id === wine.id }"
        >
          <div class="wine-image">
            <img v-if="wine.image_url" :src="wine.image_url" :alt="wine.name" />
            <div v-else class="wine-placeholder">🍷</div>
          </div>
          
          <div class="wine-info">
            <div class="wine-name">{{ wine.name }}</div>
            <div class="wine-details">
              <span v-if="wine.producer" class="producer">{{ wine.producer }}</span>
              <span v-if="wine.vintage" class="vintage">{{ wine.vintage }}</span>
              <span v-if="wine.region" class="region">{{ wine.region }}</span>
            </div>
            <div v-if="wine.wine_type_label" class="wine-type">{{ wine.wine_type_label }}</div>
            <div class="popularity">
              👥 {{ wine.recognition_count }} {{ $t('wine.recognitions') }}
            </div>
          </div>
          
          <div class="select-indicator">
            <div v-if="selectedWine?.id === wine.id" class="selected-icon">✓</div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Action buttons -->
    <div v-if="selectedWine" class="action-buttons">
      <button @click="confirmSelection" class="confirm-btn">
        {{ $t('wine.confirm_selection') }}
      </button>
      
      <button @click="clearSelection" class="cancel-btn">
        {{ $t('common.cancel') }}
      </button>
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useMultilingualContent } from '@/composables/useMultilingualContent'

export default {
  name: 'WineSelector',
  
  emits: ['wine-selected', 'selection-cancelled'],
  
  setup(props, { emit }) {
    const { t, locale } = useI18n()
    const { formatWineSearchResults } = useMultilingualContent()
    
    // Reactive data
    const searchQuery = ref('')
    const loading = ref(false)
    const showFilters = ref(false)
    const selectedWine = ref(null)
    const searchResults = ref([])
    const popularWines = ref([])
    const wineTypes = ref([])
    const wineRegions = ref([])
    
    const filters = reactive({
      wine_type: '',
      region: '',
      vintage: '',
      producer: ''
    })
    
    let searchTimeout = null
    
    // Methods
    const onSearchInput = () => {
      // Debounce search
      if (searchTimeout) {
        clearTimeout(searchTimeout)
      }
      
      searchTimeout = setTimeout(() => {
        performSearch()
      }, 300)
    }
    
    const performSearch = async () => {
      if (!searchQuery.value || searchQuery.value.trim().length < 2) {
        searchResults.value = []
        return
      }
      
      loading.value = true
      
      try {
        const params = new URLSearchParams({
          q: searchQuery.value.trim(),
          language: locale.value,
          limit: '20'
        })
        
        // Add filters
        if (filters.wine_type) params.append('wine_type', filters.wine_type)
        if (filters.region) params.append('region', filters.region)
        if (filters.vintage) params.append('vintage', filters.vintage)
        if (filters.producer) params.append('producer', filters.producer)
        
        const response = await fetch(`/api/multilingual/wines/search?${params}`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('auth-token')}`
          }
        })
        
        if (response.ok) {
          const data = await response.json()
          searchResults.value = data.results || []
        } else {
          console.error('Search failed:', response.statusText)
          searchResults.value = []
        }
      } catch (error) {
        console.error('Search error:', error)
        searchResults.value = []
      } finally {
        loading.value = false
      }
    }
    
    const loadPopularWines = async () => {
      try {
        const response = await fetch('/api/wine/popular?limit=15', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
          }
        })
        
        if (response.ok) {
          const data = await response.json()
          popularWines.value = data.wines || []
        }
      } catch (error) {
        console.error('Failed to load popular wines:', error)
      }
    }
    
    const loadWineTypes = async () => {
      try {
        const response = await fetch(`/api/multilingual/wine-types?language=${locale.value}`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('auth-token')}`
          }
        })
        
        if (response.ok) {
          const data = await response.json()
          wineTypes.value = Object.entries(data.wine_types || {}).map(([value, label]) => ({
            value,
            label
          }))
        }
      } catch (error) {
        console.error('Failed to load wine types:', error)
      }
    }
    
    const loadWineRegions = async () => {
      try {
        const response = await fetch(`/api/multilingual/regions?language=${locale.value}`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('auth-token')}`
          }
        })
        
        if (response.ok) {
          const data = await response.json()
          wineRegions.value = data.regions.map(region => ({
            value: region.code,
            label: region.name,
            wine_count: region.wine_count || 0
          }))
        }
      } catch (error) {
        console.error('Failed to load wine regions:', error)
      }
    }
    
    const selectWine = (wine) => {
      selectedWine.value = wine
    }
    
    const confirmSelection = () => {
      if (selectedWine.value) {
        emit('wine-selected', selectedWine.value)
      }
    }
    
    const clearSelection = () => {
      selectedWine.value = null
      emit('selection-cancelled')
    }
    
    const toggleFilters = () => {
      showFilters.value = !showFilters.value
    }
    
    const clearFilters = () => {
      filters.wine_type = ''
      filters.region = ''
      filters.vintage = ''
      filters.producer = ''
      performSearch()
    }
    
    // Lifecycle
    onMounted(async () => {
      await Promise.all([
        loadPopularWines(),
        loadWineTypes(),
        loadWineRegions()
      ])
    })
    
    // Watch for search query changes
    watch(searchQuery, (newQuery) => {
      if (!newQuery || newQuery.trim().length === 0) {
        searchResults.value = []
        selectedWine.value = null
      }
    })
    
    return {
      searchQuery,
      loading,
      showFilters,
      selectedWine,
      searchResults,
      popularWines,
      wineTypes,
      wineRegions,
      filters,
      onSearchInput,
      performSearch,
      selectWine,
      confirmSelection,
      clearSelection,
      toggleFilters,
      clearFilters
    }
  }
}
</script>

<style scoped>
.wine-selector {
  padding: 1rem;
  max-width: 600px;
  margin: 0 auto;
}

.search-section {
  margin-bottom: 1.5rem;
}

.search-section h3 {
  margin-bottom: 1rem;
  color: #333;
}

.search-input-container {
  position: relative;
  margin-bottom: 1rem;
}

.search-input {
  width: 100%;
  padding: 12px 40px 12px 16px;
  border: 2px solid #ddd;
  border-radius: 8px;
  font-size: 16px;
  transition: border-color 0.2s;
}

.search-input:focus {
  outline: none;
  border-color: #007bff;
}

.search-icon {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: #666;
}

.filters {
  background: #f8f9fa;
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 0.5rem;
}

.filter-row {
  display: grid;
  grid-template-columns: 1fr 1fr 120px;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.filter-select, .filter-input {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.clear-filters-btn {
  padding: 6px 12px;
  background: #6c757d;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 12px;
  cursor: pointer;
}

.toggle-filters-btn {
  padding: 8px 16px;
  background: #e9ecef;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 2rem;
  color: #666;
}

.loading-spinner {
  width: 32px;
  height: 32px;
  border: 3px solid #f3f3f3;
  border-top: 3px solid #007bff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.search-results h4, .popular-wines h4 {
  margin-bottom: 1rem;
  color: #333;
}

.wine-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.wine-item {
  display: flex;
  align-items: center;
  padding: 1rem;
  border: 2px solid #e9ecef;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.wine-item:hover {
  border-color: #007bff;
  background: #f8f9fa;
}

.wine-item.selected {
  border-color: #28a745;
  background: #d4edda;
}

.wine-image {
  width: 60px;
  height: 60px;
  margin-right: 1rem;
  flex-shrink: 0;
}

.wine-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 4px;
}

.wine-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f8f9fa;
  border-radius: 4px;
  font-size: 24px;
}

.wine-info {
  flex: 1;
}

.wine-name {
  font-weight: 600;
  font-size: 16px;
  margin-bottom: 0.25rem;
  color: #333;
}

.wine-details {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 0.25rem;
  font-size: 14px;
  color: #666;
}

.wine-details span {
  background: #e9ecef;
  padding: 2px 6px;
  border-radius: 3px;
}

.wine-type {
  font-size: 12px;
  color: #007bff;
  margin-bottom: 0.25rem;
}

.popularity {
  font-size: 12px;
  color: #28a745;
}

.select-indicator {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.selected-icon {
  width: 20px;
  height: 20px;
  background: #28a745;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: bold;
}

.no-results {
  text-align: center;
  padding: 2rem;
  color: #666;
}

.no-results-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.no-results-text {
  font-size: 18px;
  margin-bottom: 0.5rem;
}

.no-results-suggestion {
  font-size: 14px;
}

.action-buttons {
  display: flex;
  gap: 1rem;
  margin-top: 1.5rem;
  justify-content: center;
}

.confirm-btn, .cancel-btn {
  padding: 12px 24px;
  border: none;
  border-radius: 6px;
  font-size: 16px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.confirm-btn {
  background: #28a745;
  color: white;
}

.confirm-btn:hover {
  background: #218838;
}

.cancel-btn {
  background: #6c757d;
  color: white;
}

.cancel-btn:hover {
  background: #545b62;
}

@media (max-width: 768px) {
  .wine-selector {
    padding: 0.5rem;
  }
  
  .filter-row {
    grid-template-columns: 1fr;
  }
  
  .wine-item {
    padding: 0.75rem;
  }
  
  .wine-image {
    width: 50px;
    height: 50px;
  }
  
  .action-buttons {
    flex-direction: column;
  }
}
</style>