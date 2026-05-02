import logging

logger = logging.getLogger(__name__)    
table = "yt_api"

def insert_rows(cur, conn, schema, row):
    
    try:
        if schema == "staging":
            video_id = "video_id"
            
            
            cur.execute(f"""
            INSERT INTO {schema}.{table} (video_id, video_title, upload_date, duration, video_views, like_count, comment_count)
            VALUES (%(video_id)s, %(title)s, %(publishedAt)s, %(duration)s, %(viewCount)s, %(likeCount)s, %(commentCount)s);
            """, row
            )
        else:
            video_id = "video_id"
            
            cur.execute(f"""
        INSERT INTO {schema}.{table} (
            video_id, video_title, upload_date, duration,
            video_type, video_views, like_count, comment_count
        )
        VALUES (
            %(video_id)s, %(video_title)s, %(upload_date)s, %(duration)s,
            %(video_type)s, %(view_count)s, %(like_count)s, %(comment_count)s
        );
    """, row)
        conn.commit()
        
        logger.info(f"Inserted row with video_id: {row[video_id]}")

    except Exception as e:
        logger.error(f"Error inserting row with video_id: {row[video_id]}")
        raise e 
    
def update_rows(cur, conn, schema, row):
    
    try:
    # staging
        if schema == "staging":
            video_id = "video_id"
            upload_date = "publishedAt"
            video_title = "title"
            video_views = "viewCount"
            like_count = "likeCount"
            comment_count = "commentCount"
        # core
        else:
            video_id = "video_id"
            upload_date = "upload_date"
            video_title = "video_title"
            video_views = "video_views"
            like_count = "like_count"
            comment_count = "comment_count"
        
        cur.execute(f"""UPDATE {schema}.{table}     
                    set video_title = %({video_title})s, 
                    video_views = %({video_views})s, 
                    like_count = %({like_count})s, 
                    comment_count = %({comment_count})s
                    where video_id = %({video_id})s and upload_date = %({upload_date})s;
                    """, row )
    
    except Exception as e:
        logger.error(f"Error updating row with video_id: {row[video_id]}")
        raise e 

def delete_rows(cur, conn, schema, ids_to_delete):
    try:
        ids_to_delete = f"""({', '.join(f"'{id}'" for video_id in ids_to_delete)})"""
        
        cur.execute(f"""DELETE FROM {schema}.{table} WHERE video_id IN {ids_to_delete};""")
    
    except Exception as e:
        logger.error(f"Error deleting rows with video_ids: {ids_to_delete}")
        raise e 