import numpy as np
import matplotlib.pyplot as plt

# parameters for the Lorentzian (Cauchy) distribution:

x0, gamma = 0, 1  # location and scale parameters
n_samples = 100000  # Number of samples 

# Lorentzian (Cauchy) PDF:

def lorentzian_pdf(x, x0, gamma):
    return (1 / np.pi) * (gamma / ((x - x0)**2 + gamma**2))

# to generate samples using the Transformation Method:

def transform_method(size, x0, gamma):
    u = np.random.uniform(0, 1, size)
    x = x0 + gamma * np.tan(np.pi * (u - 0.5))
    return x

# for generating samples using the Accept/Reject Method:

def accept_reject(size, x0, gamma):
    samples = []
    while len(samples) < size:
        # Sample from a uniform proposal distribution:
        x_proposal = np.random.uniform(-10, 10)
        u = np.random.uniform(0, 1)

        # Maximum value of the original Lorentzian PDF:
        max_pdf = lorentzian_pdf(0, x0, gamma)  

        # Accept/reject:
        if u < lorentzian_pdf(x_proposal, x0, gamma) / max_pdf:
            samples.append(x_proposal)
    return np.array(samples)

# to generate random numbers:

samples_transform = transform_method(n_samples, x0, gamma)
samples_reject = accept_reject(n_samples, x0, gamma)

# to define the range for the plot:

x = np.linspace(-10, 10, 1000)
pdf_lorentzian = lorentzian_pdf(x, x0, gamma)

plt.figure(figsize=(12, 6))

# for plotting histogram of the transformation method samples:

plt.subplot(1, 2, 1)
plt.hist(samples_transform, bins=100, density=True, alpha=0.6, color='b', label='Transformation Method', range=(-10, 10))
plt.plot(x, pdf_lorentzian, 'r-', lw=2, label='Original PDF')
plt.title('Transformation Method')
plt.xlabel('x')
plt.ylabel('Density')
plt.legend()
plt.xlim(-10, 10)

# to plot histogram of the accept/reject method samples:

plt.subplot(1, 2, 2)
plt.hist(samples_reject, bins=100, density=True, alpha=0.6, color='g', label='Accept/Reject Method', range=(-10, 10))
plt.plot(x, pdf_lorentzian, 'r-', lw=2, label='Original PDF')
plt.title('Accept/Reject Method')
plt.xlabel('x')
plt.ylabel('Density')
plt.legend()
plt.xlim(-10, 10)


plt.tight_layout()
plt.show()
