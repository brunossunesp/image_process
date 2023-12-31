# -*- coding: utf-8 -*-
"""codigo1_pre_Processamento_Cobem_Bruno.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1qPwcKwGxKnCIsEO1qOdwwNjoWLNKmi1d
"""

from google.colab import drive
drive.mount('/content/drive')

"""################################################################################
#                                  PRÉ-PROCESSAMENTO                           #
################################################################################

## Esta seção se dedica ao processamento de imagens com o objetivo de realçar características relevantes e eliminar possíveis ruídos que possam interferir na detecção subsequente de trincas. Utilizamos três abordagens principais de suavização: filtro de média, filtro de mediana e um filtro gaussiano aplicado no domínio da frequência. Após a suavização, empregamos o algoritmo de detecção de bordas de Canny, um método popular e eficaz para identificar contornos e transições bruscas na imagem, características comumente associadas à presença de trincas ou fissuras.






"""

import cv2
import numpy as np
from matplotlib import pyplot as plt
import scipy.ndimage
from google.colab import drive
drive.mount('/content/drive')

def gaussian_kernel(size, sigma=1):
    """Retorna um kernel gaussiano 2D"""
    size = int(size) // 2
    x, y = np.mgrid[-size:size+1, -size:size+1]
    normal = 1 / (2.0 * np.pi * sigma**2)
    g =  np.exp(-((x**2 + y**2) / (2.0*sigma**2))) * normal
    return g

def fft_gaussian(img, kernel):
    """Aplica um filtro gaussiano a uma imagem no domínio da frequência"""
    img_fft = np.fft.fft2(img)
    kernel_fft = np.fft.fft2(kernel, s=img.shape)
    img_smooth = np.fft.ifft2(img_fft * kernel_fft)
    return np.abs(img_smooth)

# Carregar a imagem
img = cv2.imread('/content/drive/Othercomputers/Meu_laptop/Mestrado/imagens/rachadura_ponte.jpg')  # Troque 'sua_imagem.jpg' pelo caminho da sua imagem
img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# Aplicar os filtros de média, mediana e gaussiano
avg_blur = cv2.blur(img_gray, (5,5))  # Filtro de média com kernel 3x3
median_blur = cv2.medianBlur(img_gray, 5)  # Filtro de mediana com kernel 3x3
gaussian_blur_freq = fft_gaussian(img_gray, gaussian_kernel(5, sigma=1))  # Filtro Gaussiano no domínio da frequência

# Aplicar detecção de borda Canny
canny_avg = cv2.Canny(avg_blur, 100, 200)
canny_median = cv2.Canny(median_blur, 100, 200)
canny_gaussian_freq = cv2.Canny(gaussian_blur_freq.astype(np.uint8), 100, 200)
canny_original = cv2.Canny(img_gray, 100, 200)  # Detecção de borda Canny na imagem original

# Visualização
fig, axs = plt.subplots(1, 4, figsize=(20, 5))  # Imagens suavizadas

axs[0].imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
axs[0].set_title('Original')
axs[1].imshow(avg_blur, cmap='gray')
axs[1].set_title('Average Filter')
axs[2].imshow(median_blur, cmap='gray')
axs[2].set_title('Median Filter')
axs[3].imshow(gaussian_blur_freq, cmap='gray', vmin=0, vmax=255)
axs[3].set_title('Gaussian Filter (Frequency)')

# Desativando os eixos para todas as subplots
for ax in axs.flat:
    ax.axis('off')

plt.tight_layout()

# Salvar figura como SVG e PDF
plt.savefig('smoothed_images.svg', format='svg')
plt.savefig('smoothed_images.pdf', format='pdf')

plt.show()

fig, axs = plt.subplots(1, 5, figsize=(25, 5))  # Imagens com detecção de borda

axs[0].imshow(canny_original, cmap='gray')
axs[0].set_title('Canny on Original')
axs[1].imshow(canny_avg, cmap='gray')
axs[1].set_title('Canny on Average')
axs[2].imshow(canny_median, cmap='gray')
axs[2].set_title('Canny on Median')
axs[3].imshow(canny_gaussian_freq, cmap='gray')
axs[3].set_title('Canny on Gaussian (Frequency)')

# Desativando os eixos para todas as subplots
for ax in axs.flat:
    ax.axis('off')

plt.tight_layout()

# Salvar figura como SVG e PDF
plt.savefig('edge_detection.svg', format='svg')
plt.savefig('edge_detection.pdf', format='pdf')

plt.show()

"""################################################################################
#                          INTELIGÊNCIA DE MÁQUINA                             #
################################################################################

##Este trecho de código demonstra a aplicação de um algoritmo de classificação Máquina de Vetores de Suport (SVM) para identificar imagens que possuem ou não rachaduras. Como etapa de pré-processamento das imagens, um filtro de mediana é utilizado para suavização, seguido pela detecção de bordas usando o método Canny. O algoritmo SVM, depois de treinado, tenta prever a presença ou ausência de rachaduras com base nessas características extraídas
"""

import cv2
import numpy as np
import os
import sklearn.svm as svm
from sklearn.model_selection import train_test_split
from sklearn import metrics
import matplotlib.pyplot as plt
import seaborn as sns




# Diretórios das imagens
dir_crack = '/content/drive/Othercomputers/Meu_laptop/Mestrado/imagens/positivo-m'
dir_no_crack = '/content/drive/Othercomputers/Meu_laptop/Mestrado/imagens/negativo-m'

def process_image(image):
    """
    Função para processar uma única imagem.
    Primeiro, a imagem é convertida para escala de cinza, depois, um filtro de suavização é aplicado
    e, finalmente, a detecção de bordas é feita.
    """
    # Converta a imagem para escala de cinza
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Suavização usando filtro da mediana
    blur = cv2.medianBlur(gray,5)

    # Detecção de bordas usando Canny
    edges = cv2.Canny(blur, 100, 200)

    # Redimensionar para um tamanho fixo (100,100) para poder achatar consistentemente
    resized = cv2.resize(edges, (100,100))

    return resized

def load_images_from_folder(folder, label):
    """
    Função para carregar todas as imagens de um dado diretório (folder)
    e retornar uma lista de pares (imagem, label).
    As imagens são processadas antes de serem adicionadas à lista.
    """
    images = []
    for filename in os.listdir(folder):
        img = cv2.imread(os.path.join(folder, filename))
        if img is not None:
            img = process_image(img)
            images.append((img, label))
    return images

def flatten_images(images):
    """
    Função para achatar uma lista de imagens em uma lista de vetores.
    """
    return [img.flatten() for img in images]

# Carregando e processando as imagens
crack_images = load_images_from_folder(dir_crack, 1)
no_crack_images = load_images_from_folder(dir_no_crack, 0)

# Dividindo os dados em treinamento e teste
train_images, test_images, train_labels, test_labels = train_test_split([img[0] for img in crack_images + no_crack_images], [img[1] for img in crack_images + no_crack_images], test_size=0.2, random_state=42)

# Achatando as imagens para a lista de vetores
train_images_flat = flatten_images(train_images)
test_images_flat = flatten_images(test_images)

# Criando o classificador SVM
clf = svm.SVC()

# Treinando o classificador
clf.fit(np.array(train_images_flat), np.array(train_labels))

# Fazendo previsões
y_pred = np.squeeze((clf.predict(np.array(test_images_flat)) >= 0.5).astype(np.int))
y_certain = np.squeeze((clf.predict(np.array(test_images_flat))).astype(np.int))

# Obtendo a matriz de confusão
conf_matr = metrics.confusion_matrix(test_labels, y_pred)

# Obtendo o relatório de classificação
class_report = metrics.classification_report(test_labels, y_pred, target_names=['NEGATIVE', 'POSITIVE'])

# Exibindo o relatório de classificação
print("\nClassification Report:")
print(class_report)

# Plotando a matriz de confusão como um heatmap
plt.figure(figsize=(6,6))
sns.heatmap(conf_matr, fmt='g', annot=True, annot_kws={"size": 14}, cbar=False, vmin=0, cmap='Blues')
plt.xticks(ticks=np.arange(2) + 0.5, labels=['NEGATIVE', 'POSITIVE'])
plt.yticks(ticks=np.arange(2) + 0.5, labels=['NEGATIVE', 'POSITIVE'])
plt.xlabel('Predicted')
plt.ylabel('Actual')
plt.title('Confusion Matrix')
plt.show()