import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from face_analysis import get_pred_label, draw_label

def display_initial_image(img):
    plt.figure(figsize=(5,5))
    plt.imshow(img)
    plt.title('Original Image')
    plt.axis('off')
    plt.show(block=False)
    plt.pause(0.001)
    print("Displayed original image for uploaded file")

def display_final_results(results):
    n_faces = len(results)
    if n_faces > 0:
        fig, axes = plt.subplots(n_faces, 2, figsize=(12, 6 * n_faces))
        if n_faces == 1:
            axes = [axes]
        for i, (original_face, enhanced_face, result_original, result_enhanced) in enumerate(results):
            label_original = get_pred_label(result_original)
            label_enhanced = get_pred_label(result_enhanced)
            original_labeled = draw_label(original_face, label_original)
            enhanced_labeled = draw_label(enhanced_face, label_enhanced)

            axes[i][0].imshow(original_labeled)
            axes[i][0].set_title(f"Original Face {i+1} Prediction")
            axes[i][0].axis('off')
            axes[i][1].imshow(enhanced_labeled)
            axes[i][1].set_title(f"Enhanced Face {i+1} Prediction")
            axes[i][1].axis('off')

            print(f"Face {i+1} - Original Image Prediction:\n", label_original)
            print(f"Face {i+1} - Enhanced Image Prediction:\n", label_enhanced)
        plt.tight_layout()
        plt.show(block=True)
        print("Displayed final prediction plots for captured faces")
    plt.close('all')