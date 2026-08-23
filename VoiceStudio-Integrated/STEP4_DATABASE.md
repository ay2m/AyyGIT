# Step 4: Database Layer Implementation
## VoiceStudio Database Architecture
قاعدة البيانات - Database Layer

### Overview

Step 4 implements a comprehensive SQLite database layer, replacing the file-based storage system with proper relational database operations. This provides:

- **Persistent Storage**: All voice models stored in SQLite database
- **Transaction Support**: ACID compliance for merge operations
- **Efficient Querying**: Indexed queries for filtering and pagination
- **History Tracking**: Complete merge and synthesis history
- **Backup & Recovery**: Database backup and integrity verification
- **Scalability**: Ready for PostgreSQL migration in production

### Database Schema

#### 1. voice_models Table
Primary table storing voice model metadata:
```sql
CREATE TABLE voice_models (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    language TEXT NOT NULL DEFAULT 'ar',
    sample_rate INTEGER DEFAULT 16000,
    duration REAL DEFAULT 0.0,
    file_size INTEGER DEFAULT 0,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    voice_type TEXT DEFAULT 'original',  -- original/merged/cloned
    quality_score REAL DEFAULT 0.0,
    tags TEXT,  -- JSON array
    audio_file_path TEXT,
    features_data TEXT  -- JSON with acoustic features
)
```

**Key Features**:
- UUID primary key for global uniqueness
- Stored acoustic features (spectral_centroid, pitch, energy, etc.)
- File path reference to audio files
- JSON tags for flexible categorization
- Quality score for voice evaluation

#### 2. merge_history Table
Tracks voice merging operations:
```sql
CREATE TABLE merge_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    merged_voice_id TEXT NOT NULL,
    source_voice_ids TEXT NOT NULL,  -- JSON array
    weights TEXT,  -- JSON array of blend weights
    created_at TEXT NOT NULL,
    FOREIGN KEY (merged_voice_id) REFERENCES voice_models(id)
)
```

**Purpose**:
- Maintains lineage of merged voices
- Records which voices were combined and their weights
- Enables voice provenance tracking

#### 3. synthesis_history Table
Logs all text-to-speech synthesis operations:
```sql
CREATE TABLE synthesis_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    voice_id TEXT NOT NULL,
    text TEXT NOT NULL,
    language TEXT NOT NULL,
    generated_at TEXT NOT NULL,
    duration REAL,
    audio_file_path TEXT,
    FOREIGN KEY (voice_id) REFERENCES voice_models(id)
)
```

**Purpose**:
- Tracks synthesis usage per voice
- Records generated text and audio references
- Supports analytics and auditing

### VoiceStudioDB Class

#### Core Methods

**Connection Management**:
```python
get_connection()      # Get/create database connection
close()              # Close connection
verify_database()    # Verify integrity
```

**Voice Model Operations**:
```python
save_voice_model(voice, audio_path, features)  # Store new/updated voice
get_voice_model(voice_id)                       # Retrieve voice metadata
get_voice_features(voice_id)                    # Get acoustic features
get_voice_audio_path(voice_id)                  # Get audio file path
list_voice_models(language, voice_type, skip, limit)  # Query with filters
count_voice_models(language, voice_type)        # Total count
delete_voice_model(voice_id)                    # Remove voice
```

**Merge History**:
```python
save_merge_history(merged_id, source_ids, weights)  # Log merge operation
get_merge_history(merged_id)                        # Retrieve merge info
```

**Synthesis History**:
```python
save_synthesis_history(voice_id, text, language, duration, path)  # Log synthesis
get_synthesis_history(voice_id, limit)                            # Retrieve logs
```

**Backup & Maintenance**:
```python
export_backup(backup_path)  # Create database backup
verify_database()           # Check integrity (PRAGMA integrity_check)
```

### API Endpoints (New & Updated)

#### Updated Endpoints

**POST /voices/create**
- Now saves to database instead of JSON files
- Stores acoustic features in features_data column
- Maintains audio files in ./voices/audio/

**GET /voices**
- Queries database with filters
- Supports language and voice_type filtering
- Efficient pagination with database queries

**GET /voices/{voice_id}**
- Retrieves from database
- Returns all stored metadata

**DELETE /voices/{voice_id}**
- Removes from database
- Cascading delete for merge/synthesis history

**POST /voices/merge**
- Saves merged voice to database
- Logs merge operation in merge_history table

**POST /synthesis/voice**
- Saves synthesis to synthesis_history table
- Retrieves features from database

#### New Database Endpoints

**GET /voices/{voice_id}/merge-history**
```json
{
  "voice_id": "...",
  "is_merged": true,
  "source_voices": ["voice_id1", "voice_id2"],
  "weights": [0.6, 0.4],
  "merged_at": "2026-08-23T..."
}
```

**GET /voices/{voice_id}/synthesis-history**
```json
{
  "voice_id": "...",
  "voice_name": "Arabic Voice",
  "total_syntheses": 42,
  "syntheses": [
    {
      "text": "مرحبا",
      "language": "ar",
      "generated_at": "2026-08-23T...",
      "duration": 2.5
    }
  ]
}
```

**POST /database/backup**
- Creates timestamped backup in ./voices/backups/
- Returns backup metadata

**GET /database/verify**
- Checks database integrity
- Reports valid/corrupted status

**GET /database/stats**
- Returns database statistics
- Counts by voice type
- Database file size

### Storage Structure

```
VoiceStudio-Integrated/
├── voices/
│   ├── voicestudio.db          # Main SQLite database
│   ├── audio/                  # Audio files directory
│   │   ├── {voice_id}.wav
│   │   └── ...
│   └── backups/                # Backup directory
│       ├── backup_2026-08-23T...db
│       └── ...
└── database.py                 # Database layer implementation
```

### Data Flow

#### Voice Creation
1. User uploads audio → Core engine extracts features
2. VoiceModel created with quality score
3. Acoustic features serialized to JSON
4. `save_voice_model()` stores in database with features_data
5. Audio file saved to disk, path stored in database

#### Voice Merging
1. Load source voices from database
2. Retrieve audio files using stored paths
3. Engine blends audio and features
4. `save_voice_model()` stores merged voice
5. `save_merge_history()` logs operation with source IDs

#### Text-to-Speech Synthesis
1. Retrieve voice from database
2. Load features using `get_voice_features()`
3. Engine generates audio with voice characteristics
4. `save_synthesis_history()` logs text, duration, language
5. Return audio with voice metadata headers

### Migration from File-Based Storage

#### For Existing Deployments

If migrating from file-based storage:

```python
# Initialize database
db = VoiceStudioDB()

# Load existing voice from JSON metadata
for metadata_file in METADATA_DIR.glob("*.json"):
    with open(metadata_file) as f:
        model_data = json.load(f)
    
    voice_id = model_data['id']
    audio_path = AUDIO_DIR / f"{voice_id}.wav"
    
    # Save to database
    voice = VoiceModel(**model_data)
    db.save_voice_model(voice, str(audio_path))
```

### Performance Characteristics

**Query Performance**:
- Indexed by language, voice_type, created_at
- Pagination handled by SQL LIMIT/OFFSET
- Direct database queries vs. file I/O

**Storage Efficiency**:
- Single database file vs. multiple JSON files
- Reduced disk I/O
- Efficient blob storage for audio references

**Scalability**:
- SQLite suitable for development/small deployments
- Ready for PostgreSQL backend in production
- Connection pooling for concurrent requests

### Production Deployment

#### PostgreSQL Migration

For production environments, switch to PostgreSQL:

```python
# Update database.py for PostgreSQL
import psycopg2

class VoiceStudioDB:
    def __init__(self, connection_string):
        self.conn = psycopg2.connect(connection_string)
```

#### Backup Strategy

Recommended backup schedule:
- Daily incremental backups
- Weekly full backups
- Off-site replication for critical data
- Automated backup verification

### Error Handling

Database operations include error handling for:
- Connection failures
- Data integrity violations
- Concurrent access conflicts
- File system errors (audio not found)

All operations return boolean success status or raise HTTPException with details.

### Future Enhancements

**Phase 2**:
- User authentication with user_voices table
- Voice version control (track modifications)
- Batch synthesis operations
- Advanced analytics (usage patterns, popular voices)

**Phase 3**:
- Full-text search on voice descriptions
- Recommendation engine based on synthesis history
- Multi-language support optimization
- Performance profiling and indexing optimization
