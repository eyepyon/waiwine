"""
Wine Data Seeder for populating the database with sample wine data.
"""
import uuid
import logging
from typing import List, Dict, Any
from sqlalchemy.orm import Session

from backend.models.wine import Wine, Translation
from backend.utils.database import get_db

logger = logging.getLogger(__name__)

class WineDataSeeder:
    """Service for seeding wine data into the database."""
    
    def __init__(self):
        pass
    
    def seed_sample_wines(self) -> bool:
        """Seed the database with sample wine data."""
        try:
            db = next(get_db())
            
            # Check if wines already exist
            existing_count = db.query(Wine).count()
            if existing_count > 0:
                logger.info(f"Database already contains {existing_count} wines. Skipping seeding.")
                return True
            
            sample_wines = self._get_sample_wine_data()
            
            for wine_data in sample_wines:
                wine = Wine(**wine_data)
                db.add(wine)
            
            db.commit()
            
            logger.info(f"Successfully seeded {len(sample_wines)} sample wines")
            return True
            
        except Exception as e:
            logger.error(f"Failed to seed wine data: {e}")
            return False
    
    def seed_wine_type_translations(self) -> bool:
        """Seed wine type translations."""
        try:
            db = next(get_db())
            
            # Check if translations already exist
            existing_count = db.query(Translation).filter(
                Translation.key.like('wine.type.%')
            ).count()
            
            if existing_count > 0:
                logger.info("Wine type translations already exist. Skipping seeding.")
                return True
            
            translations = self._get_wine_type_translations()
            
            for translation_data in translations:
                translation = Translation(**translation_data)
                db.add(translation)
            
            db.commit()
            
            logger.info(f"Successfully seeded {len(translations)} wine type translations")
            return True
            
        except Exception as e:
            logger.error(f"Failed to seed wine type translations: {e}")
            return False
    
    def _get_sample_wine_data(self) -> List[Dict[str, Any]]:
        """Get sample wine data."""
        return [
            {
                'id': str(uuid.uuid4()),
                'name': 'Château Margaux',
                'producer': 'Château Margaux',
                'vintage': 2015,
                'region': 'Bordeaux',
                'wine_type': 'red',
                'alcohol_content': 13.5,
                'name_translations': {
                    'ja': 'シャトー・マルゴー',
                    'en': 'Château Margaux',
                    'ko': '샤토 마르고'
                },
                'tasting_notes_translations': {
                    'ja': 'エレガントで複雑な赤ワイン。カシスとスパイスの香り。',
                    'en': 'Elegant and complex red wine with cassis and spice notes.',
                    'ko': '우아하고 복잡한 레드 와인. 카시스와 스파이스 향.'
                },
                'recognition_keywords': ['Margaux', 'Château', 'Bordeaux'],
                'recognition_count': 15
            },
            {
                'id': str(uuid.uuid4()),
                'name': 'Dom Pérignon',
                'producer': 'Moët & Chandon',
                'vintage': 2012,
                'region': 'Champagne',
                'wine_type': 'sparkling',
                'alcohol_content': 12.5,
                'name_translations': {
                    'ja': 'ドン・ペリニヨン',
                    'en': 'Dom Pérignon',
                    'ko': '돔 페리뇽'
                },
                'tasting_notes_translations': {
                    'ja': '洗練されたシャンパーニュ。繊細な泡と果実味。',
                    'en': 'Refined champagne with delicate bubbles and fruit flavors.',
                    'ko': '세련된 샴페인. 섬세한 거품과 과일 맛.'
                },
                'recognition_keywords': ['Dom Pérignon', 'Moët', 'Champagne'],
                'recognition_count': 23
            },
            {
                'id': str(uuid.uuid4()),
                'name': 'Opus One',
                'producer': 'Opus One Winery',
                'vintage': 2018,
                'region': 'Napa Valley',
                'wine_type': 'red',
                'alcohol_content': 14.5,
                'name_translations': {
                    'ja': 'オーパス・ワン',
                    'en': 'Opus One',
                    'ko': '오퍼스 원'
                },
                'tasting_notes_translations': {
                    'ja': 'カベルネ・ソーヴィニヨン主体の力強い赤ワイン。',
                    'en': 'Powerful red wine dominated by Cabernet Sauvignon.',
                    'ko': '카베르네 소비뇽 주체의 강력한 레드 와인.'
                },
                'recognition_keywords': ['Opus One', 'Napa', 'Cabernet'],
                'recognition_count': 18
            },
            {
                'id': str(uuid.uuid4()),
                'name': 'Chablis Premier Cru',
                'producer': 'William Fèvre',
                'vintage': 2020,
                'region': 'Burgundy',
                'wine_type': 'white',
                'alcohol_content': 13.0,
                'name_translations': {
                    'ja': 'シャブリ・プルミエ・クリュ',
                    'en': 'Chablis Premier Cru',
                    'ko': '샤블리 프리미에 크뤼'
                },
                'tasting_notes_translations': {
                    'ja': 'ミネラル豊富な辛口白ワイン。牡蠣との相性抜群。',
                    'en': 'Mineral-rich dry white wine, perfect with oysters.',
                    'ko': '미네랄이 풍부한 드라이 화이트 와인. 굴과 완벽한 조화.'
                },
                'recognition_keywords': ['Chablis', 'Premier Cru', 'Fèvre'],
                'recognition_count': 12
            },
            {
                'id': str(uuid.uuid4()),
                'name': 'Barolo Brunate',
                'producer': 'Giuseppe Rinaldi',
                'vintage': 2017,
                'region': 'Piedmont',
                'wine_type': 'red',
                'alcohol_content': 14.0,
                'name_translations': {
                    'ja': 'バローロ・ブルナーテ',
                    'en': 'Barolo Brunate',
                    'ko': '바롤로 브루나테'
                },
                'tasting_notes_translations': {
                    'ja': 'ネッビオーロ100%の伝統的なバローロ。長期熟成可能。',
                    'en': '100% Nebbiolo traditional Barolo with aging potential.',
                    'ko': '네비올로 100%의 전통적인 바롤로. 장기 숙성 가능.'
                },
                'recognition_keywords': ['Barolo', 'Brunate', 'Rinaldi', 'Nebbiolo'],
                'recognition_count': 8
            },
            {
                'id': str(uuid.uuid4()),
                'name': 'Sancerre',
                'producer': 'Henri Bourgeois',
                'vintage': 2021,
                'region': 'Loire Valley',
                'wine_type': 'white',
                'alcohol_content': 12.5,
                'name_translations': {
                    'ja': 'サンセール',
                    'en': 'Sancerre',
                    'ko': '상세르'
                },
                'tasting_notes_translations': {
                    'ja': 'ソーヴィニヨン・ブラン100%。爽やかな酸味とハーブの香り。',
                    'en': '100% Sauvignon Blanc with fresh acidity and herbal notes.',
                    'ko': '소비뇽 블랑 100%. 상쾌한 산미와 허브 향.'
                },
                'recognition_keywords': ['Sancerre', 'Bourgeois', 'Sauvignon'],
                'recognition_count': 14
            },
            {
                'id': str(uuid.uuid4()),
                'name': 'Rioja Gran Reserva',
                'producer': 'Marqués de Riscal',
                'vintage': 2015,
                'region': 'Rioja',
                'wine_type': 'red',
                'alcohol_content': 13.5,
                'name_translations': {
                    'ja': 'リオハ・グラン・レセルバ',
                    'en': 'Rioja Gran Reserva',
                    'ko': '리오하 그란 레세르바'
                },
                'tasting_notes_translations': {
                    'ja': 'テンプラニーリョ主体。長期熟成による複雑な味わい。',
                    'en': 'Tempranillo-based with complex flavors from extended aging.',
                    'ko': '템프라니요 주체. 장기 숙성으로 인한 복잡한 맛.'
                },
                'recognition_keywords': ['Rioja', 'Gran Reserva', 'Riscal', 'Tempranillo'],
                'recognition_count': 11
            },
            {
                'id': str(uuid.uuid4()),
                'name': 'Riesling Kabinett',
                'producer': 'Dr. Loosen',
                'vintage': 2020,
                'region': 'Mosel',
                'wine_type': 'white',
                'alcohol_content': 8.5,
                'name_translations': {
                    'ja': 'リースリング・カビネット',
                    'en': 'Riesling Kabinett',
                    'ko': '리슬링 카비네트'
                },
                'tasting_notes_translations': {
                    'ja': '軽やかで甘みのあるリースリング。アペリティフに最適。',
                    'en': 'Light and off-dry Riesling, perfect as an aperitif.',
                    'ko': '가볍고 약간 단 리슬링. 아페리티프로 완벽.'
                },
                'recognition_keywords': ['Riesling', 'Kabinett', 'Loosen', 'Mosel'],
                'recognition_count': 9
            },
            {
                'id': str(uuid.uuid4()),
                'name': 'Chianti Classico',
                'producer': 'Antinori',
                'vintage': 2019,
                'region': 'Tuscany',
                'wine_type': 'red',
                'alcohol_content': 13.5,
                'name_translations': {
                    'ja': 'キャンティ・クラシコ',
                    'en': 'Chianti Classico',
                    'ko': '키안티 클라시코'
                },
                'tasting_notes_translations': {
                    'ja': 'サンジョヴェーゼ主体。チェリーとスパイスの香り。',
                    'en': 'Sangiovese-based with cherry and spice aromas.',
                    'ko': '산지오베제 주체. 체리와 스파이스 향.'
                },
                'recognition_keywords': ['Chianti', 'Classico', 'Antinori', 'Sangiovese'],
                'recognition_count': 16
            },
            {
                'id': str(uuid.uuid4()),
                'name': 'Prosecco di Valdobbiadene',
                'producer': 'Bisol',
                'vintage': 2021,
                'region': 'Veneto',
                'wine_type': 'sparkling',
                'alcohol_content': 11.5,
                'name_translations': {
                    'ja': 'プロセッコ・ディ・ヴァルドッビアーデネ',
                    'en': 'Prosecco di Valdobbiadene',
                    'ko': '프로세코 디 발도비아데네'
                },
                'tasting_notes_translations': {
                    'ja': '軽やかなスパークリングワイン。フレッシュな果実味。',
                    'en': 'Light sparkling wine with fresh fruit flavors.',
                    'ko': '가벼운 스파클링 와인. 신선한 과일 맛.'
                },
                'recognition_keywords': ['Prosecco', 'Valdobbiadene', 'Bisol'],
                'recognition_count': 20
            }
        ]
    
    def _get_wine_type_translations(self) -> List[Dict[str, Any]]:
        """Get wine type translations."""
        translations = []
        
        wine_types = {
            'wine.type.red': {
                'ja': '赤ワイン',
                'en': 'Red Wine',
                'ko': '레드 와인',
                'es': 'Vino Tinto',
                'fr': 'Vin Rouge',
                'de': 'Rotwein'
            },
            'wine.type.white': {
                'ja': '白ワイン',
                'en': 'White Wine',
                'ko': '화이트 와인',
                'es': 'Vino Blanco',
                'fr': 'Vin Blanc',
                'de': 'Weißwein'
            },
            'wine.type.rose': {
                'ja': 'ロゼワイン',
                'en': 'Rosé Wine',
                'ko': '로제 와인',
                'es': 'Vino Rosado',
                'fr': 'Vin Rosé',
                'de': 'Roséwein'
            },
            'wine.type.sparkling': {
                'ja': 'スパークリングワイン',
                'en': 'Sparkling Wine',
                'ko': '스파클링 와인',
                'es': 'Vino Espumoso',
                'fr': 'Vin Effervescent',
                'de': 'Schaumwein'
            },
            'wine.type.dessert': {
                'ja': 'デザートワイン',
                'en': 'Dessert Wine',
                'ko': '디저트 와인',
                'es': 'Vino de Postre',
                'fr': 'Vin de Dessert',
                'de': 'Dessertwein'
            },
            'wine.type.fortified': {
                'ja': '酒精強化ワイン',
                'en': 'Fortified Wine',
                'ko': '주정강화 와인',
                'es': 'Vino Fortificado',
                'fr': 'Vin Fortifié',
                'de': 'Likörwein'
            }
        }
        
        for key, language_values in wine_types.items():
            for language, value in language_values.items():
                translations.append({
                    'key': key,
                    'language': language,
                    'value': value
                })
        
        return translations

# Service instance
wine_data_seeder = WineDataSeeder()