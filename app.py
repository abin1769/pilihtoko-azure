from flask import Flask, render_template, request, url_for, jsonify
from collections import deque
import os
import sys
import re

sys.path.append('.')

# Import modules
from modules.dijkstra_graf import dijkstra_graf
from modules.data_loader import load_data
from modules.fuzzy import hitung_kecocokan

app = Flask(__name__)

# --- Memuat Data Baru ---
try:
    graf_jalan = load_data('data/graf_jalan.json')
    grid_visual = load_data('data/map.json')
    rumah_data = load_data('data/rumah.json')
    toko_data = load_data('data/toko.json')
except FileNotFoundError as e:
    print(f"Error: File data tidak ditemukan - {e}")
    sys.exit(1)

# Membuat daftar barang (tidak berubah)
all_items = set()
for data in toko_data.values():
    if 'stok' in data and isinstance(data['stok'], dict):
        all_items.update(data['stok'].keys())
barang_list = sorted(list(all_items))

# --- FUNGSI HELPER BARU UNTUK SINGKATAN NODE ---
def get_node_abbreviation(node_name):
    """Mengembalikan singkatan untuk nama node."""
    # Coba cari angka di akhir nama node
    match = re.search(r'(\d+)$', node_name) # Cari satu atau lebih digit di akhir string
    number_suffix = match.group(1) if match else '' # Ambil angka jika ditemukan

    if node_name.startswith("Rumah"):
        return f"R{number_suffix}" if number_suffix else "R"
    elif node_name.startswith("Simpang"):
        return f"S{number_suffix}" if number_suffix else "S"
    elif node_name.startswith("Toko"):
        return f"T{number_suffix}" if number_suffix else "T"
            
    # Jika tidak sesuai pola di atas, coba ambil beberapa karakter pertama atau kembalikan nama asli
    if len(node_name) > 4:
        return node_name[:4] + "..."
    return node_name # Kembalikan nama asli jika sangat pendek atau tidak cocok

# Daftarkan fungsi helper ke Jinja2 agar bisa dipanggil di template HTML
app.jinja_env.globals.update(get_node_abbreviation=get_node_abbreviation)


def build_visual_path(path_nodes, start_node_name):
    """
    Helper function untuk membangun visual path dari abstract path nodes.
    """
    visual_path = []
    if path_nodes and len(path_nodes) > 1:
        for i in range(len(path_nodes) - 1):
            segment_start_name = path_nodes[i]
            segment_end_name = path_nodes[i+1]
            
            if segment_start_name not in graf_jalan['nodes'] or segment_end_name not in graf_jalan['nodes']:
                visual_path = []
                break
            
            visual_segment = get_visual_path(segment_start_name, segment_end_name, graf_jalan['nodes'], grid_visual)
            
            if not visual_segment:
                visual_path = []
                break

            if i > 0 and visual_segment and visual_path and visual_segment[0] == visual_path[-1]:
                visual_segment.pop(0)
            
            visual_path.extend(visual_segment)
    elif path_nodes and len(path_nodes) == 1:
        if start_node_name in graf_jalan['nodes']:
            visual_path.append(list(graf_jalan['nodes'][start_node_name]))
    
    return visual_path


# --- FUNGSI HELPER BARU UNTUK VISUALISASI JALUR PADA GRID ---
def get_visual_path(start_node_name, end_node_name, graph_nodes, grid):
    """
    Menggunakan BFS pada grid untuk mencari jalur visual antara dua titik.
    """
    if start_node_name not in graph_nodes or end_node_name not in graph_nodes:
        return []

    start_coord = tuple(graph_nodes[start_node_name])
    end_coord = tuple(graph_nodes[end_node_name])

    # Validasi koordinat dalam batas grid
    if not (0 <= start_coord[1] < len(grid) and 0 <= start_coord[0] < len(grid[0])):
        return []
    if not (0 <= end_coord[1] < len(grid) and 0 <= end_coord[0] < len(grid[0])):
        return []
    
    # Validasi koordinat tidak di tembok
    if grid[start_coord[1]][start_coord[0]] == 0 or grid[end_coord[1]][end_coord[0]] == 0:
        return []

    queue = deque([(start_coord, [start_coord])])
    visited = {start_coord}
    
    while queue:
        (x, y), path = queue.popleft()
        
        if (x, y) == end_coord:
            return path

        moves = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if 0 <= ny < len(grid) and 0 <= nx < len(grid[0]):
                if grid[ny][nx] != 0 and (nx, ny) not in visited:
                    visited.add((nx, ny))
                    new_path = list(path)
                    new_path.append((nx, ny))
                    queue.append(((nx, ny), new_path))
    
    return []


@app.route('/')
def home():
    return render_template('home.html', 
                           rumah_list=rumah_data.keys(), 
                           barang_list=barang_list, 
                           toko=toko_data, 
                           title="Pencarian Toko Sembako")

@app.route('/rekomendasi', methods=['POST'])
def rekomendasi():
    mode = request.form.get('mode_pencarian')

    if mode == 'rekomendasi_barang':
        rumah_dipilih = request.form.get('rumah_mode1')
        barang_dicari = request.form.get('barang', '').lower()
        
        if not rumah_dipilih or rumah_dipilih not in rumah_data:
            return render_template('home.html', rumah_list=rumah_data.keys(), barang_list=barang_list, toko=toko_data, error="Rumah tidak valid.")


        skor_tiap_toko = {}
        for nama_toko, data_toko in toko_data.items():
            stok_total = data_toko.get("stok", {}).get(barang_dicari, 0)
            if stok_total == 0:
                continue
            
            jarak, path_nodes, _ = dijkstra_graf(graf_jalan, rumah_dipilih, nama_toko) # Ambil 3 nilai, abaikan yang terakhir
            if jarak == float('inf'):
                continue

            rating = data_toko.get("rating", 0)
            skor, alasan = hitung_kecocokan(jarak, rating, stok_total)
            
            visual_path = build_visual_path(path_nodes, rumah_dipilih)

            # Siapkan toko_info_for_js terpisah untuk kebutuhan JavaScript
            toko_info_for_js = {
                "nama": nama_toko,
                "lokasi": data_toko["lokasi"],
                "jalur": visual_path
            }

            skor_tiap_toko[nama_toko] = {
                "skor": skor, "jarak": jarak, "alasan": alasan, 
                "stok": stok_total, "rating": rating,
                "lokasi": data_toko["lokasi"],
                "jalur": visual_path,
                "toko_info_for_js": toko_info_for_js
            }

        rekomendasi_sorted = sorted(skor_tiap_toko.items(), key=lambda x: -x[1]["skor"])[:3]
        return render_template('rekomendasi.html',
                               rekomendasi=rekomendasi_sorted,
                               barang=barang_dicari,
                               rumah=rumah_dipilih,
                               rumah_asal={'nama': rumah_dipilih, 'lokasi': rumah_data[rumah_dipilih]},
                               grid=grid_visual,
                               map_image_url=url_for('static', filename='img/denah_peta.png'),
                               title="Hasil Rekomendasi")

    elif mode == 'toko_terdekat':
        rumah_dipilih = request.form.get('rumah_mode2')
        if not rumah_dipilih or rumah_dipilih not in rumah_data:
            return render_template('home.html', rumah_list=rumah_data.keys(), barang_list=barang_list, toko=toko_data, error="Rumah tidak valid.")

        toko_data_list = []
        for nama_toko, data_toko in toko_data.items():
            jarak, path_nodes, _ = dijkstra_graf(graf_jalan, rumah_dipilih, nama_toko)
            
            if jarak != float('inf'):
                visual_path = build_visual_path(path_nodes, rumah_dipilih)

                # Siapkan toko_info_for_js terpisah untuk kebutuhan JavaScript
                toko_info_for_js = {
                    "nama": nama_toko,
                    "lokasi": data_toko["lokasi"],
                    "jalur": visual_path
                }

                toko_data_list.append({
                    "nama": nama_toko, "jarak": jarak,
                    "rating": data_toko.get("rating", "N/A"),
                    "lokasi": data_toko["lokasi"],
                    "jalur": visual_path,
                    "toko_info_for_js": toko_info_for_js
                })
        
        toko_terdekat_sorted = sorted(toko_data_list, key=lambda x: x["jarak"])
        
        return render_template('hasil_terdekat.html', 
                               toko_list=toko_terdekat_sorted, 
                               rumah_asal={'nama': rumah_dipilih, 'lokasi': rumah_data[rumah_dipilih]},
                               grid=grid_visual,
                               map_image_url=url_for('static', filename='img/denah_peta.png'),
                               semua_rumah=rumah_data,
                               semua_toko=toko_data,
                               title="Daftar Toko Terdekat")

    elif mode == 'rute_spesifik':
        rumah_dipilih = request.form.get('rumah_mode3')
        toko_dipilih = request.form.get('toko')
        if not rumah_dipilih or rumah_dipilih not in rumah_data or \
           not toko_dipilih or toko_dipilih not in toko_data:
            return render_template('home.html', rumah_list=rumah_data.keys(), barang_list=barang_list, toko=toko_data, error="Pilihan rumah atau toko tidak valid.")


        jarak, path_nodes, _ = dijkstra_graf(graf_jalan, rumah_dipilih, toko_dipilih)
        visual_path = build_visual_path(path_nodes, rumah_dipilih)
            
        return render_template('hasil_rute.html',
                               jarak=jarak, jalur=visual_path,
                               rumah={'nama': rumah_dipilih, 'lokasi': rumah_data[rumah_dipilih]},
                               toko={'nama': toko_dipilih, 'lokasi': toko_data[toko_dipilih]['lokasi']},
                               grid=grid_visual,
                               semua_rumah=rumah_data, 
                               semua_toko=toko_data,
                               map_image_url=url_for('static', filename='img/denah_peta.png'),
                               title=f"Rute dari {rumah_dipilih} ke {toko_dipilih}")

    return "Mode pencarian tidak valid.", 400

@app.route('/harga')
def harga_sembako():
     return render_template('harga.html', title="Harga Sembako")

@app.route('/how', methods=['GET'])
def how_it_works():
    return render_template('how_it_works.html', 
                           grid=grid_visual, 
                           semua_rumah=rumah_data, 
                           semua_toko=toko_data,
                           map_image_url=url_for('static', filename='img/denah_peta.png'),
                           all_graph_nodes=graf_jalan['nodes'], 
                           all_graph_adjacency=graf_jalan['adjacency'], 
                           title="Cara Kerja Algoritma")

@app.route('/get_dijkstra_steps', methods=['POST'])
def get_dijkstra_steps():
    try:
        data = request.get_json()
        start_node_name = data['start_node_name']
        end_node_name = data['end_node_name']



        if start_node_name not in graf_jalan['nodes'] or end_node_name not in graf_jalan['nodes']:
            return jsonify({"error": "Start or end node not found in graph."}), 400

        jarak, path_nodes_abstract, dijkstra_steps_data = dijkstra_graf(graf_jalan, start_node_name, end_node_name)

        if jarak == float('inf'):
            return jsonify({"error": "No path found in abstract graph."}), 404
        
        # Bangun visual path
        visual_path = []
        if path_nodes_abstract and len(path_nodes_abstract) > 1:
            for i in range(len(path_nodes_abstract) - 1):
                segment_start_name = path_nodes_abstract[i]
                segment_end_name = path_nodes_abstract[i+1]
                
                if segment_start_name not in graf_jalan['nodes'] or segment_end_name not in graf_jalan['nodes']:
                    return jsonify({"error": f"Node '{segment_start_name}' or '{segment_end_name}' in path has no visual coordinates."}), 500

                visual_segment = get_visual_path(segment_start_name, segment_end_name, graf_jalan['nodes'], grid_visual)
                
                if not visual_segment:
                    return jsonify({"error": f"No visual path found for segment '{segment_start_name}' to '{segment_end_name}' on the grid."}), 500

                if i > 0 and visual_segment and visual_segment[0] == visual_path[-1]:
                    visual_segment.pop(0)
                
                visual_path.extend(visual_segment)
        elif path_nodes_abstract and len(path_nodes_abstract) == 1:
            if start_node_name in graf_jalan['nodes']:
                visual_path.append(list(graf_jalan['nodes'][start_node_name]))
            else:
                return jsonify({"error": f"Start node '{start_node_name}' has no visual coordinates."}), 500
        # Modifikasi dijkstra_steps_data untuk menggunakan singkatan
        processed_dijkstra_steps = []
        for step in dijkstra_steps_data:
            processed_step = dict(step)
            processed_step["unvisited_q"] = [get_node_abbreviation(n) for n in step["unvisited_q"]]
            processed_step["visited_s"] = [get_node_abbreviation(n) for n in step["visited_s"]]
            processed_step["current_node"] = get_node_abbreviation(step["current_node"]) if step["current_node"] else None
            processed_node_states = {}
            for node_name_full, state in step["node_states"].items():
                processed_state = dict(state)
                if processed_state["prev"] is not None:
                    processed_state["prev"] = get_node_abbreviation(processed_state["prev"])
                processed_node_states[get_node_abbreviation(node_name_full)] = processed_state
            processed_step["node_states"] = processed_node_states
            processed_dijkstra_steps.append(processed_step)

        return jsonify({
            "path": visual_path,
            "distance": jarak,
            "start_node_location": graf_jalan['nodes'][start_node_name],
            "end_node_location": graf_jalan['nodes'][end_node_name],
            "dijkstra_steps": processed_dijkstra_steps,
        })
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500

# --- Rute Baru untuk Halaman Info ---
@app.route('/info')
def about_app():
    return render_template('info.html', title="Tentang Aplikasi")

if __name__ == '__main__':
    # Azure App Service akan menggunakan environment variable PORT
    port = int(os.environ.get('PORT', 8000))
    # Untuk production, set debug=False
    debug_mode = os.environ.get('FLASK_ENV') != 'production'
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
