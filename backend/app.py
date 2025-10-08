import os
import pandas
from flask import Flask
from flask_cors import CORS 
import yfinance as yf
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from scipy.optimize import minimize


