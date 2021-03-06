#ifndef _GPS_H
#define _GPS_H
#include <iostream>
#include <vector>
#include <memory>
#include <chrono>
#include <cmath>
#include <Eigen/Dense>

#include "./include/LBFGS++/LBFGS.h"


// Declare namespace for Gaussian process definitions
namespace GP {

  // Define PI using arctan function
  static const double PI = std::atan(1)*4;

  // Define aliases with using declarations
  using Matrix = Eigen::MatrixXd;
  using Vector = Eigen::VectorXd;

  // Define function for retrieving time from chrono
  float getTime(std::chrono::high_resolution_clock::time_point start, std::chrono::high_resolution_clock::time_point end);
  using time = std::chrono::high_resolution_clock::time_point;
  using std::chrono::high_resolution_clock;

  // Define linspace function for generating equally spaced points 
  Matrix linspace(double a, double b, int N, int dim=1);

  // Define function for sampling uniform distribution on interval
  Matrix sampleUnif(double a=0.0, double b=1.0, int N=1, int dim=1);
  Vector sampleUnifVector(Vector lbs, Vector ubs);
  Matrix sampleNormal(int N=1);
  
  // Define utility functions for computing distance matrices
  void pdist(Matrix & Dv, Matrix & X1, Matrix & X2);
  void squareForm(Matrix & D, Matrix & Dv, int n, double diagVal=0.0);

  
  // Define abstract base class for covariance kernels
  class Kernel 
  {    
  public:

    // Constructor and destructor
    Kernel(Vector p, int c) : kernelParams(p) , paramCount(c) { };
    virtual ~Kernel() = default;

    // Compute the covariance matrix provided input observations and kernel hyperparameters
    virtual void computeCov(Matrix & K, Matrix & obsX, Vector & params, std::vector<Matrix> & gradList, double jitter, bool evalGrad) =0;

    // Compute the (cross-)covariance matrix for specified input vectors X1 and X2
    virtual void computeCrossCov(Matrix & K, Matrix & X1, Matrix & X2, Vector & params) = 0;

    // Set the noise level which is to be added to the diagonal of the covariance matrix
    void setNoise(double noise) { noiseLevel = noise; fixedNoise = true; }

    // Set the scaling level which is to be multiplied into the non-noise terms of the covariance matrix
    void setScaling(double scaling) { scalingLevel = scaling; fixedScaling = true; }

    // Set method for specifying the kernel parameters
    void setParams(Vector params) { kernelParams = params; };

    // Get methods for retrieving the kernel paramaters
    int getParamCount() { return paramCount; } ;
    Vector getParams() { return kernelParams; };

  protected:
    Vector kernelParams;
    int paramCount;
    double noiseLevel;
    double scalingLevel;
    bool fixedNoise = false;
    bool fixedScaling = false;
    //double parseParams(const Vector & params, Vector & kernelParams);
    //std::vector<double> parseParams(const Vector & params, Vector & kernelParams);
    void parseParams(const Vector & params, Vector & kernelParams, std::vector<double> & nonKernelParams);
    //virtual double evalKernel(Matrix&, Matrix&, Vector&, int) = 0;
    virtual double evalDistKernel(double, Vector&, int) = 0;
  };


  // Define class for radial basis function (RBF) covariance kernel
  class RBF : public Kernel
  {
  public:

    // Constructor
    RBF() : Kernel(Vector(1), 1) { kernelParams(0)=1.0; };
    
    // Compute the covariance matrix provided input observations and kernel hyperparameters
    void computeCov(Matrix & K, Matrix & obsX, Vector & params, std::vector<Matrix> & gradList, double jitter, bool evalGrad);
    // Compute the (cross-)covariance matrix for specified input vectors X1 and X2
    void computeCrossCov(Matrix & K, Matrix & X1, Matrix & X2, Vector & params);
    
  private:

    // Functions for evaluating the kernel on a pair of points / a specified squared distance
    //double evalKernel(Matrix&, Matrix&, Vector&, int);
    double evalDistKernel(double, Vector&, int);
    
  };



  
  // Define class for Gaussian processes
  class GaussianProcess
  {    
  public:

    // Constructor
    GaussianProcess() { }

    // Copy Constructor
    GaussianProcess(const GaussianProcess & m) { std::cout << "\n [*] WARNING: copy constructor called by GaussianProcess\n"; }
    
    // Define LBFGS++ function call for optimization
    double operator()(const Eigen::VectorXd& p, Eigen::VectorXd& g) { return evalNLML(p, g, true); }
    
    // Set methods
    void setObs(Matrix & x, Matrix & y) { obsX = x; obsY = y; } 
    void setKernel(Kernel & k) { kernel = &k; }
    void setPred(Matrix & px) { predX = px; }
    void setNoise(double noise) { fixedNoise = true; noiseLevel = noise; }
    void setBounds(Vector & lbs, Vector & ubs) { lowerBounds = lbs; upperBounds = ubs; fixedBounds=true; }
    void setSolverIterations(int i) { solverIterations = i; };
    void setSolverPrecision(double p) { solverPrecision = p; };
    void setSolverRestarts(int n) { solverRestarts = n; };

    // Compute methods
    void fitModel();
    void predict();
    double computeNLML(const Vector & p);
    double computeNLML();
    
    // Get methods    
    Matrix getPredMean() { return predMean; }
    Matrix getPredVar() { return predCov.diagonal() + noiseLevel*Eigen::VectorXd::Ones(predMean.size()); }
    Matrix getSamples(int count=10);
    Vector getParams() { return (*kernel).getParams(); }
    double getNoise() { return noiseLevel; }
    double getScaling() { return scalingLevel; }
    

  private:

    // Specify whether or not to display debugging and time diagnostic information
    bool VERBOSE = false;
    
    // Private member functions
    double evalNLML(const Vector & p); 
    double evalNLML(const Vector & p, Vector & g, bool evalGrad=false);
    
    // Kernel and covariance matrix
    Kernel * kernel;
    double noiseLevel = 0.0;
    bool fixedNoise = false;
    double scalingLevel = 1.0;
    bool fixedScaling = false;
    double jitter = 1e-10;

    // Store Cholsky decomposition
    Eigen::LLT<Matrix> cholesky;

    // Hyperparameter bounds
    Vector lowerBounds;
    Vector upperBounds;
    bool fixedBounds = false;
    void parseBounds(Vector & lbs, Vector & ubs, int augParamCount);
    int solverIterations = 1000;
    //double solverPrecision = 1e8;
    double solverPrecision = 1e8;
    double solverRestarts = 0;
      
    // Store squared distance matrix and alpha for NLML/DNLML calculations
    Matrix alpha;
    
    // Observation data
    Matrix obsX; 
    Matrix obsY; 
    
    // Prediction data
    Matrix predX;
    Matrix predMean;
    Matrix predCov;
    double NLML = 0.0;

    
    // Utility function for determining "augmented" solver parameter count
    int getAugParamCount(int count);

    int paramCount;
    int augParamCount;

    // Need to find a way to avoid creating new gradList each time...
    std::vector<Matrix> gradList;  

    // DEFINE TIMER VARIABLES
    ///*
    double time_computecov = 0.0;
    double time_cholesky_llt = 0.0;
    double time_alpha = 0.0;
    double time_NLML = 0.0;
    double time_term = 0.0;
    double time_grad = 0.0;
    double time_evaluation = 0.0;
    //*/
    
    // Count gradient evaluations by optimizer
    int gradientEvals = 0;

  };

  
};

//   ------------  CppOptLib Implementation  ------------  //

// Include CppOptLib files
//#include "./include/cppoptlib/meta.h"
//#include "./include/cppoptlib/boundedproblem.h"
//#include "./include/cppoptlib/solver/lbfgsbsolver.h"

// class GaussianProcess : public cppoptlib::BoundedProblem<double>

// Define alias for base class CppOptLib "BoundedProblem" for use in initialization list
// using Superclass = cppoptlib::BoundedProblem<double>;
    
// Constructors  [ Initialize lowerBounds / upperBounds of CppOptLib superclass to zero ]
// GaussianProcess() : Superclass(Vector(0), Vector(0)) { }

// Define CppOptLib methods
// [ 'value' returns NLML and 'gradient' asigns the associated gradient vector to 'g' ]
// double value(const Vector &p) { return evalNLML(p, cppOptLibgrad, true); }
// void gradient(const Vector &p, Vector &g) { g = cppOptLibgrad; }
// Vector cppOptLibgrad;


#endif
