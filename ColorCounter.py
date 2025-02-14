import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from PIL import Image, ImageTk
import numpy as np
from collections import Counter
from sklearn.cluster import KMeans
import os

def open_image():
    file_path = filedialog.askopenfilename()
    if file_path:
        load_image(file_path)

def load_image(file_path):
    global img, img_array, img_label
    img = Image.open(file_path)
    img = img.convert('RGB')  # Ensure image is in RGB format
    img.thumbnail((400, 400))
    img_tk = ImageTk.PhotoImage(img)
    img_label.config(image=img_tk)
    img_label.image = img_tk
    
    img_array = np.array(img)
    process_image()

def process_image():
    global img_array, accuracy_slider, color_frame, accuracy_entry, kmeans_entry, mode_var, processed_image
    if img_array is None:
        return

    data = img_array.reshape((-1, 3)) / 255.0

    if mode_var.get() == "accuracy":
        accuracy = accuracy_slider.get()
        num_clusters = max(1, accuracy // 5)
    else:
        num_clusters = int(kmeans_entry.get())
    
    kmeans = KMeans(n_clusters=num_clusters)
    kmeans.fit(data)
    cluster_centers = kmeans.cluster_centers_
    labels = kmeans.labels_

    color_counts = Counter(labels)
    cluster_centers = (cluster_centers * 255).astype(int)
    
    # Create the processed image
    new_image_array = cluster_centers[labels].reshape(img_array.shape)
    processed_image = Image.fromarray(new_image_array.astype('uint8'))

    for widget in color_frame.winfo_children():
        widget.destroy()

    for idx, count in color_counts.items():
        color = cluster_centers[idx]
        hex_color = '#{:02x}{:02x}{:02x}'.format(*color)
        
        # Calculate luminance to decide text color
        luminance = 0.299 * color[0] + 0.587 * color[1] + 0.114 * color[2]
        text_color = "black" if luminance > 128 else "white"

        color_label = tk.Label(color_frame, text=f"{hex_color}: {count}", bg=hex_color, fg=text_color)
        color_label.pack(fill='x')

def save_image():
    if processed_image is None:
        return
    file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png"), ("All files", "*.*")])
    if file_path:
        processed_image.save(file_path)

def update_accuracy_from_entry(event):
    try:
        accuracy_value = int(accuracy_entry.get())
        if 0 <= accuracy_value <= 255:
            accuracy_slider.set(accuracy_value)
            process_image()
    except ValueError:
        pass

def update_accuracy_from_slider(value):
    accuracy_entry.delete(0, tk.END)
    accuracy_entry.insert(0, str(value))
    process_image()

def update_kmeans_clusters(event):
    try:
        kmeans_value = int(kmeans_entry.get())
        if kmeans_value > 0:
            process_image()
    except ValueError:
        pass

def switch_mode():
    if mode_var.get() == "accuracy":
        accuracy_slider.config(state="normal")
        accuracy_entry.config(state="normal")
        kmeans_entry.config(state="disabled")
    else:
        accuracy_slider.config(state="disabled")
        accuracy_entry.config(state="disabled")
        kmeans_entry.config(state="normal")
    process_image()

# Create main window
root = tk.Tk()
root.title("Image Color Counter")

# Create UI elements
open_button = tk.Button(root, text="Open Image", command=open_image)
open_button.pack()

mode_var = tk.StringVar(value="accuracy")

accuracy_mode = tk.Radiobutton(root, text="Accuracy Mode", variable=mode_var, value="accuracy", command=switch_mode)
accuracy_mode.pack()

accuracy_label = tk.Label(root, text="Accuracy:")
accuracy_label.pack()

accuracy_slider = tk.Scale(root, from_=0, to=255, orient=tk.HORIZONTAL, command=update_accuracy_from_slider)
accuracy_slider.set(128)
accuracy_slider.pack()

accuracy_entry = tk.Entry(root)
accuracy_entry.insert(0, "128")
accuracy_entry.bind("<Return>", update_accuracy_from_entry)
accuracy_entry.pack()

kmeans_mode = tk.Radiobutton(root, text="Direct KMeans Mode", variable=mode_var, value="kmeans", command=switch_mode)
kmeans_mode.pack()

kmeans_entry = tk.Entry(root)
kmeans_entry.insert(0, "6")
kmeans_entry.bind("<Return>", update_kmeans_clusters)
kmeans_entry.pack()
kmeans_entry.config(state="disabled")

save_button = tk.Button(root, text="Save Processed Image", command=save_image)
save_button.pack()

img_label = tk.Label(root)
img_label.pack()

color_frame = tk.Frame(root)
color_frame.pack(fill='both', expand=True)

img = None
img_array = None
processed_image = None

root.mainloop()
