from flask import Flask, request, send_file, jsonify, send_from_directory
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend
import matplotlib.pyplot as plt
from PIL import Image
import matplotlib.animation as animation

app = Flask(__name__)

# Output directory
output_dir = os.path.join(app.instance_path, '3d')
os.makedirs(output_dir, exist_ok=True)

# Upload Image Endpoint
@app.route('/upload_image', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in request'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    img_path = os.path.join(output_dir, file.filename)
    file.save(img_path)
    return jsonify({'message': 'Image uploaded successfully', 'filename': file.filename})

# Generate and Save 3D Plot Based on Image
@app.route('/generate_plot/<filename>', methods=['POST'])
def generate_plot(filename):
    try:
        # Load the uploaded image
        img_path = os.path.join(output_dir, filename)
        img = Image.open(img_path).convert('L')  # Convert to grayscale
        img_array = np.array(img)

        # Generate a 3D plot using image pixel values
        x = np.linspace(0, img_array.shape[1], img_array.shape[1])
        y = np.linspace(0, img_array.shape[0], img_array.shape[0])
        X, Y = np.meshgrid(x, y)
        Z = img_array  # Use pixel intensities as Z-axis values

        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        ax.plot_surface(X, Y, Z, cmap='viridis')

        # Save the plot
        plot_filename = os.path.join(output_dir, f'plot_{filename}.png')
        plt.savefig(plot_filename, dpi=75)
        plt.close()

        return jsonify({'message': '3D plot generated successfully', 'plot_path': plot_filename})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Generate 3D Animated GIF Based on Image
@app.route('/generate_gif/<filename>', methods=['POST'])
def generate_gif(filename):
    try:
        # Load the uploaded image
        img_path = os.path.join(output_dir, filename)
        img = Image.open(img_path).convert('L')  # Convert to grayscale
        img_array = np.array(img)

        # Generate frames for GIF
        x = np.linspace(0, img_array.shape[1], img_array.shape[1])
        y = np.linspace(0, img_array.shape[0], img_array.shape[0])
        X, Y = np.meshgrid(x, y)
        Z = img_array  # Use pixel intensities as Z-axis values

        fig = plt.figure(figsize=(6, 6))
        ax = fig.add_subplot(111, projection='3d')

        def update(frame):
            ax.clear()
            ax.plot_surface(X, Y, Z * np.sin(frame / 10), cmap='viridis')
            ax.view_init(30, frame)

        ani = animation.FuncAnimation(fig, update, frames=60, interval=50)
        gif_filename = os.path.join(output_dir, f'gif_{filename}.gif')
        ani.save(gif_filename, writer='pillow', fps=10)

        return jsonify({'message': 'GIF generated successfully', 'gif_path': gif_filename})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Serve Images
@app.route('/images/<filename>')
def get_image(filename):
    return send_from_directory(output_dir, filename)


from flask import Flask, render_template

@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
