# --- DOWNLOAD & STITCHING ---
@st.cache_data(show_spinner=False, ttl=CACHE_TTL)
def get_stitched_image(image_id):
    base_url = f"https://iiif-antenati.cultura.gov.it/iiif/2/{image_id}"
    info_resp = requests.get(f"{base_url}/info.json", headers=HEADERS)
    info_resp.raise_for_status()
    info = info_resp.json()
    
    w, h = info["width"], info["height"]
    
    # Corrected extraction logic for tile dimensions
    first_tile = info["tiles"][0]
    tw = first_tile["width"]
    th = first_tile.get("height", tw) # Use width if height isn't specified
    
    final_img = Image.new("RGB", (w, h))
    cols, rows = math.ceil(w / tw), math.ceil(h / th)
    total_tiles = rows * cols
    
    progress_placeholder = st.empty()
    tile_count = 0
    for r in range(rows):
        for c in range(cols):
            tile_count += 1
            x, y = c * tw, r * th
            tile_w, tile_h = min(tw, w - x), min(th, h - y)
            tile_url = f"{base_url}/{x},{y},{tile_w},{tile_h}/full/0/default.jpg"
            progress_placeholder.progress(tile_count / total_tiles, text=f"📥 Downloading tile {tile_count} of {total_tiles}...")
            res = requests.get(tile_url, headers=HEADERS)
            tile_data = Image.open(BytesIO(res.content))
            final_img.paste(tile_data, (x, y))
    
    progress_placeholder.empty()
    buf = BytesIO()
    final_img.save(buf, format="JPEG", quality=95)
    return buf.getvalue()
