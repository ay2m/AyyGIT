"""
VoiceStudio Database Layer
قاعدة بيانات VoiceStudio
"""

import sqlite3
import json
import numpy as np
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import asdict
from core_engine import VoiceModel, VoiceFeatures, Language


class VoiceStudioDB:
    """SQLite database for VoiceStudio voice models"""

    def __init__(self, db_path: str = "./voices/voicestudio.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = None
        self.init_db()

    def get_connection(self):
        """Get or create database connection"""
        if self.conn is None:
            self.conn = sqlite3.connect(str(self.db_path))
            self.conn.row_factory = sqlite3.Row
        return self.conn

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            self.conn = None

    def init_db(self):
        """Initialize database schema"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Voice models table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS voice_models (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                language TEXT NOT NULL DEFAULT 'ar',
                sample_rate INTEGER DEFAULT 16000,
                duration REAL DEFAULT 0.0,
                file_size INTEGER DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                voice_type TEXT DEFAULT 'original',
                quality_score REAL DEFAULT 0.0,
                tags TEXT,
                audio_file_path TEXT,
                features_data TEXT
            )
        """)

        # Voice merging history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS merge_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                merged_voice_id TEXT NOT NULL,
                source_voice_ids TEXT NOT NULL,
                weights TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (merged_voice_id) REFERENCES voice_models(id)
            )
        """)

        # Synthesis history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS synthesis_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                voice_id TEXT NOT NULL,
                text TEXT NOT NULL,
                language TEXT NOT NULL,
                generated_at TEXT NOT NULL,
                duration REAL,
                audio_file_path TEXT,
                FOREIGN KEY (voice_id) REFERENCES voice_models(id)
            )
        """)

        # Create indexes for common queries
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_voice_language ON voice_models(language)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_voice_type ON voice_models(voice_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_voice_created ON voice_models(created_at)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_synthesis_voice ON synthesis_history(voice_id)")

        conn.commit()

    def save_voice_model(self, voice_model: VoiceModel, audio_file_path: Optional[str] = None, features: Optional[VoiceFeatures] = None) -> bool:
        """Save voice model to database"""
        conn = self.get_connection()
        cursor = conn.cursor()

        features_data = None
        if features:
            features_dict = {
                'spectral_centroid': float(features.spectral_centroid),
                'spectral_rolloff': float(features.spectral_rolloff),
                'zero_crossing_rate': float(features.zero_crossing_rate),
                'pitch_mean': float(features.pitch_mean),
                'pitch_variance': float(features.pitch_variance),
                'energy': float(features.energy)
            }
            features_data = json.dumps(features_dict)

        try:
            cursor.execute("""
                INSERT OR REPLACE INTO voice_models
                (id, name, description, language, sample_rate, duration, file_size,
                 created_at, updated_at, voice_type, quality_score, tags, audio_file_path, features_data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                voice_model.id,
                voice_model.name,
                voice_model.description,
                voice_model.language.value,
                voice_model.sample_rate,
                voice_model.duration,
                voice_model.file_size,
                voice_model.created_at,
                voice_model.updated_at,
                voice_model.voice_type,
                voice_model.quality_score,
                json.dumps(voice_model.tags),
                audio_file_path,
                features_data
            ))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error saving voice model: {e}")
            return False

    def get_voice_model(self, voice_id: str) -> Optional[VoiceModel]:
        """Retrieve voice model from database"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, name, description, language, sample_rate, duration, file_size,
                   created_at, updated_at, voice_type, quality_score, tags, audio_file_path, features_data
            FROM voice_models WHERE id = ?
        """, (voice_id,))

        row = cursor.fetchone()
        if not row:
            return None

        voice_model = VoiceModel(
            id=row['id'],
            name=row['name'],
            description=row['description'],
            language=Language(row['language']),
            sample_rate=row['sample_rate'],
            duration=row['duration'],
            file_size=row['file_size'],
            created_at=row['created_at'],
            updated_at=row['updated_at'],
            voice_type=row['voice_type'],
            quality_score=row['quality_score'],
            tags=json.loads(row['tags']) if row['tags'] else []
        )
        return voice_model

    def get_voice_features(self, voice_id: str) -> Optional[VoiceFeatures]:
        """Retrieve voice features from database"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT features_data FROM voice_models WHERE id = ?", (voice_id,))
        row = cursor.fetchone()

        if not row or not row['features_data']:
            return None

        try:
            features_dict = json.loads(row['features_data'])
            # Reconstruct MFCC as placeholder (13 coefficients)
            mfcc = np.zeros((13, 1))

            return VoiceFeatures(
                mfcc=mfcc,
                spectral_centroid=features_dict['spectral_centroid'],
                spectral_rolloff=features_dict['spectral_rolloff'],
                zero_crossing_rate=features_dict['zero_crossing_rate'],
                pitch_mean=features_dict['pitch_mean'],
                pitch_variance=features_dict['pitch_variance'],
                energy=features_dict['energy']
            )
        except Exception as e:
            print(f"Error loading features: {e}")
            return None

    def get_voice_audio_path(self, voice_id: str) -> Optional[str]:
        """Get audio file path for voice model"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT audio_file_path FROM voice_models WHERE id = ?", (voice_id,))
        row = cursor.fetchone()
        return row['audio_file_path'] if row else None

    def list_voice_models(self, language: Optional[str] = None, voice_type: Optional[str] = None,
                         skip: int = 0, limit: int = 10) -> List[VoiceModel]:
        """List voice models with optional filters"""
        conn = self.get_connection()
        cursor = conn.cursor()

        query = "SELECT * FROM voice_models WHERE 1=1"
        params = []

        if language:
            query += " AND language = ?"
            params.append(language)

        if voice_type:
            query += " AND voice_type = ?"
            params.append(voice_type)

        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, skip])

        cursor.execute(query, params)
        rows = cursor.fetchall()

        voices = []
        for row in rows:
            voice_model = VoiceModel(
                id=row['id'],
                name=row['name'],
                description=row['description'],
                language=Language(row['language']),
                sample_rate=row['sample_rate'],
                duration=row['duration'],
                file_size=row['file_size'],
                created_at=row['created_at'],
                updated_at=row['updated_at'],
                voice_type=row['voice_type'],
                quality_score=row['quality_score'],
                tags=json.loads(row['tags']) if row['tags'] else []
            )
            voices.append(voice_model)
        return voices

    def delete_voice_model(self, voice_id: str) -> bool:
        """Delete voice model from database"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # Delete synthesis history first
            cursor.execute("DELETE FROM synthesis_history WHERE voice_id = ?", (voice_id,))

            # Delete merge history
            cursor.execute("DELETE FROM merge_history WHERE merged_voice_id = ? OR source_voice_ids LIKE ?",
                          (voice_id, f'%"{voice_id}"%'))

            # Delete voice model
            cursor.execute("DELETE FROM voice_models WHERE id = ?", (voice_id,))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error deleting voice model: {e}")
            return False

    def save_merge_history(self, merged_voice_id: str, source_voice_ids: List[str],
                          weights: Optional[List[float]] = None) -> bool:
        """Save voice merge history"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO merge_history (merged_voice_id, source_voice_ids, weights, created_at)
                VALUES (?, ?, ?, ?)
            """, (
                merged_voice_id,
                json.dumps(source_voice_ids),
                json.dumps(weights) if weights else None,
                datetime.utcnow().isoformat()
            ))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error saving merge history: {e}")
            return False

    def get_merge_history(self, merged_voice_id: str) -> Optional[Dict[str, Any]]:
        """Get merge history for a voice"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT source_voice_ids, weights, created_at FROM merge_history
            WHERE merged_voice_id = ? ORDER BY created_at DESC LIMIT 1
        """, (merged_voice_id,))

        row = cursor.fetchone()
        if not row:
            return None

        return {
            'source_voice_ids': json.loads(row['source_voice_ids']),
            'weights': json.loads(row['weights']) if row['weights'] else None,
            'created_at': row['created_at']
        }

    def save_synthesis_history(self, voice_id: str, text: str, language: str,
                              duration: float = 0.0, audio_file_path: Optional[str] = None) -> bool:
        """Save synthesis history"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO synthesis_history (voice_id, text, language, generated_at, duration, audio_file_path)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                voice_id,
                text,
                language,
                datetime.utcnow().isoformat(),
                duration,
                audio_file_path
            ))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error saving synthesis history: {e}")
            return False

    def get_synthesis_history(self, voice_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get synthesis history for a voice"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT text, language, generated_at, duration FROM synthesis_history
            WHERE voice_id = ? ORDER BY generated_at DESC LIMIT ?
        """, (voice_id, limit))

        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    def count_voice_models(self, language: Optional[str] = None, voice_type: Optional[str] = None) -> int:
        """Count voice models with optional filters"""
        conn = self.get_connection()
        cursor = conn.cursor()

        query = "SELECT COUNT(*) as count FROM voice_models WHERE 1=1"
        params = []

        if language:
            query += " AND language = ?"
            params.append(language)

        if voice_type:
            query += " AND voice_type = ?"
            params.append(voice_type)

        cursor.execute(query, params)
        return cursor.fetchone()['count']

    def export_backup(self, backup_path: str) -> bool:
        """Create database backup"""
        try:
            conn = self.get_connection()
            backup_conn = sqlite3.connect(backup_path)
            with backup_conn:
                conn.backup(backup_conn)
            backup_conn.close()
            return True
        except Exception as e:
            print(f"Error creating backup: {e}")
            return False

    def verify_database(self) -> bool:
        """Verify database integrity"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("PRAGMA integrity_check")
            result = cursor.fetchone()[0]
            return result == "ok"
        except Exception as e:
            print(f"Database integrity check failed: {e}")
            return False
