from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import shutil
import tempfile
from pathlib import Path
from transfer import organize_webp_folders
from organize import organize_webp_files

app = Flask(__name__)
CORS(app)  # Restrict to Vercel domain

@app.route('/organize', methods=['POST'])
def organize():
    try:
        temp_dir = Path(tempfile.mkdtemp())
        webp_folder = temp_dir / "__WEBP To be move to the right folders"
        webp_folder.mkdir()
        files = request.files.getlist('files')
        for file in files:
            file_path = webp_folder / file.filename
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file.save(file_path)
        success = organize_webp_files(str(webp_folder))
        file_structure = []
        for root, dirs, files in os.walk(webp_folder):
            for file in files:
                file_structure.append(os.path.relpath(os.path.join(root, file), temp_dir))
        shutil.rmtree(temp_dir)
        return jsonify({
            'status': 'success' if success else 'failed',
            'message': 'Organization completed successfully' if success else 'Organization failed',
            'files': file_structure
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/transfer', methods=['POST'])
def transfer():
    try:
        temp_dir = Path(tempfile.mkdtemp())
        main_folder = temp_dir / "main"
        main_folder.mkdir()
        webp_folder = main_folder / "__WEBP To be move to the right folders"
        webp_folder.mkdir()
        files = request.files.getlist('files')
        for file in files:
            file_path = webp_folder / file.filename
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file.save(file_path)
        organize_webp_folders(str(main_folder))
        file_structure = []
        for root, dirs, files in os.walk(main_folder):
            for file in files:
                file_structure.append(os.path.relpath(os.path.join(root, file), temp_dir))
        shutil.rmtree(temp_dir)
        return jsonify({
            'status': 'success',
            'message': 'Transfer completed successfully',
            'files': file_structure
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/test', methods=['GET'])
def test():
    return jsonify({'status': 'success', 'message': 'Backend is running'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
