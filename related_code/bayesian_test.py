'''
Mar 2019 by Sebastiano Barbieri
s.barbieri@unsw.edu.au
'''
from __future__ import print_function
import torch
import numpy as np
import scipy.stats as st
from hyperparameters import Hyperparameters as hp
from data_load import *
from modules import *
import os
from tqdm import tqdm
from train import Net
import matplotlib.pyplot as plt
from sklearn.metrics import *
from sklearn.calibration import calibration_curve
from bayesian_train import *
from pdb import set_trace as bp

def round(num):
  return np.round(num*1000)/1000

if __name__ == '__main__':
  # Load data
  print('Load data...')
  data = np.load(hp.data_dir + 'data_arrays.npz')
  
  # Test data
  testloader, num_batches, pos_weight = get_trainloader(data, 'TEST', shuffle=False)

  # Vocabulary sizes
  num_static = num_static(data)
  num_dp_codes, num_cp_codes = vocab_sizes(data)

  # CUDA for PyTorch
  use_cuda = torch.cuda.is_available()
  device = torch.device('cuda:0' if use_cuda else 'cpu')
  hp.device = device
  torch.backends.cudnn.benchmark = True

  # Network
  net = BayesianNetwork(num_static, num_dp_codes, num_cp_codes, pos_weight, num_batches).to(device)
  
  print('Evaluate...')
  # Set log dir to read trained model from
  logdir = hp.logdir + 'bayesian/'

  # Restore variables from disk
  net.load_state_dict(torch.load(logdir + 'final_model.pt', map_location=device))

  # evaluate on validation data
  net.eval()
  label_pred = torch.Tensor([])
  label_test = torch.Tensor([])
  with torch.no_grad():
    for i, (stat, dp, cp, dp_t, cp_t, label_batch) in enumerate(tqdm(testloader), 0):
      # move to GPU if available
      stat  = stat.to(device)
      dp    = dp.to(device)
      cp    = cp.to(device)
      dp_t  = dp_t.to(device)
      cp_t  = cp_t.to(device)

      for i in tqdm(range(hp.test_samples)):
        label_pred_batch, _ = net(stat, dp, cp, dp_t, cp_t, sample=True)
        label_pred = torch.cat((label_pred, label_pred_batch.cpu()))
      label_test = torch.cat((label_test, label_batch))

  label_sigmoids = torch.sigmoid(label_pred).view(-1, hp.test_samples, hp.batch_size).mean(dim=1).view(-1).cpu().numpy()  
  
  # Average precision
  avpre = average_precision_score(label_test, label_sigmoids)
  
  # Determine AUROC score
  auroc = roc_auc_score(label_test, label_sigmoids)
  
  # Sensitivity, specificity
  fpr, tpr, thresholds = roc_curve(label_test, label_sigmoids)
  youden_idx = np.argmax(tpr - fpr)
  sensitivity = tpr[youden_idx]
  specificity = 1-fpr[youden_idx]

  # F1 score
  f1_final = 0
  for t in thresholds:
    label_pred = (np.array(label_sigmoids) >= t).astype(int)
    f1 = f1_score(label_test, label_pred)
    if f1 > f1_final:
      f1_final = f1
  f1 = f1_final
  
  # Calibration
  # fraction_of_positives, mean_predicted_value = calibration_curve(label_test, label_sigmoids, n_bins=10)
  # plt.plot([0, 1], [0, 1], 'k:', label='Perfectly calibrated')
  # plt.plot(mean_predicted_value, fraction_of_positives, 's-', label=hp.net_variant)
  # ax = plt.gca()
  # ax.set_xlabel('Mean Predicted Probability')
  # ax.set_ylabel('True Probability (Fractions of Positives)')
  # ax.set_ylim([-0.05, 1.05])
  # ax.legend(loc='upper left')
  # ax.set_title('Calibration plots (reliability curve)')
  # plt.show()
  
  print('------------------------------------------------')
  print('Net variant: bayesian')
  print('Mean Average Precision score: {}'.format(round(avpre)))
  print('Mean AUROC score: {}'.format(round(auroc)))
  print('Mean Sensitivity: {}'.format(round(sensitivity)))
  print('Mean Specificity: {}'.format(round(specificity)))
  print('Mean F1: {}'.format(round(f1)))
  print('Done')
  

