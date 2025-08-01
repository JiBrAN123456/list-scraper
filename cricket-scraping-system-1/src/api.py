class WebAPI:
    """Optional web API for accessing scraped data"""
    
    def __init__(self, db_manager):
        self.db = db_manager
    
    def get_live_matches(self) -> List[Dict]:
        """Get currently live matches"""
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT m.*, ls.score, ls.overs, ls.run_rate 
            FROM matches m
            LEFT JOIN live_scores ls ON m.match_id = ls.match_id
            WHERE m.status = 'Live'
            ORDER BY ls.timestamp DESC
        ''')
        
        matches = []
        for row in cursor.fetchall():
            match = {
                'match_id': row[0],
                'title': row[1],
                'team1': row[2],
                'team2': row[3],
                'venue': row[4],
                'current_score': row[13] if row[13] else 'Not Started',
                'overs': row[14] if row[14] else '0.0',
                'run_rate': row[15] if row[15] else '0.0'
            }
            matches.append(match)
        
        conn.close()
        return matches
    
    def get_match_details(self, match_id: str) -> Dict:
        """Get detailed information for a specific match"""
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        # Get match info
        cursor.execute('SELECT * FROM matches WHERE match_id = ?', (match_id,))
        match_row = cursor.fetchone()
        
        if not match_row:
            return {}
        
        # Get latest live score
        cursor.execute('''
            SELECT * FROM live_scores 
            WHERE match_id = ? 
            ORDER BY timestamp DESC 
            LIMIT 1
        ''', (match_id,))
        live_row = cursor.fetchone()
        
        # Get squads
        cursor.execute('SELECT * FROM squads WHERE match_id = ?', (match_id,))
        squad_rows = cursor.fetchall()
        
        conn.close()
        
        return {
            'match_info': {
                'match_id': match_row[0],
                'title': match_row[1],
                'team1': match_row[2],
                'team2': match_row[3],
                'venue': match_row[4],
                'date': match_row[5],
                'time': match_row[6],
                'status': match_row[8]
            },
            'live_score': {
                'score': live_row[5] if live_row else None,
                'overs': live_row[6] if live_row else None,
                'run_rate': live_row[7] if live_row else None,
                'last_updated': live_row[10] if live_row else None
            } if live_row else None,
            'squads': [
                {
                    'team_name': row[2],
                    'players': json.loads(row[3]) if row[3] else [],
                    'captain': row[4],
                    'wicket_keeper': row[5]
                }
                for row in squad_rows
            ]
        }