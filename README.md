# mini-alpha-zero
Implemented alpha zero and the go game to play from scratch to play/test on a smaller board with size 4x4, 5x5, 6x6, 7x7, 8x8. It is reproduced using MCTS with CNN.

# dependency
pandas
numpy
pytorch
pickle

# file location
all training temp data is saved at ./train

all model data is saved at ./models

all plot data is saved at ./plots

# to run the project
To test go game run:
```console
py ./game_test.py

```
To train all sizes of models run:
```console
py ./train.py
```

To test all sizes on baseline model run:
```console
py ./test.py 
```

