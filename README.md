# image_process
Detecção de Trincas em Imagens
Este software tem como objetivo detectar trincas em imagens por meio de técnicas avançadas de pré-processamento e inteligência de máquina. Ele é composto por duas etapas principais:

Pré-processamento de Imagens: Envolve a suavização das imagens usando diferentes métodos (média, mediana e gaussiano) seguido por detecção de bordas usando o algoritmo Canny.

Inteligência de Máquina: Utiliza o algoritmo SVM (Support Vector Machines) para classificar as imagens com base nas características extraídas na fase de pré-processamento.

Dependências
OpenCV (cv2)
NumPy (numpy)
Matplotlib (matplotlib)
Scipy (scipy.ndimage)
Google Colab (google.colab)
scikit-learn (sklearn.svm, sklearn.model_selection, sklearn.metrics)
Seaborn (seaborn)
Como usar
Carregue sua imagem principal para a parte de pré-processamento.
Forneça um conjunto de imagens (banco de imagens) para treinamento e teste para a etapa de Inteligência de Máquina.
Execute o código. As imagens resultantes após o pré-processamento e os resultados da classificação serão exibidos.
Nota
A imagem principal deve ser inserida na primeira parte do código.
Um conjunto de imagens é necessário para treinar e testar o modelo SVM na segunda parte do código.
Autor
Bruno Soares
