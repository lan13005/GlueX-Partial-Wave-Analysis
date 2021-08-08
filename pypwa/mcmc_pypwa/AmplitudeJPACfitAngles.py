import numpy as npy
from typing import Dict
import scipy.special

import PyPWA as pwa
from dataclasses import dataclass
import pandas

import numexpr as ne

## Fitting ##

class FitAmplitude(pwa.NestedFunction):


    def __init__(self, initial_params):
        self.__elm = self.make_elm(initial_params)

    def setup(self, kVars):
        self.__kVars = kVars
        self.__decay = self.__produce_specific_decay()

    @staticmethod
    def make_elm(params):
        # Number of parameters
        length = int(len(params) / 2)

        # Produce ELM Dataframe
        elm = npy.empty(length, [("e", int), ("l", int), ("m", int)])
        elm = pandas.DataFrame(elm)

        # Extract ELM values from minuit parameters
        values = []
        for param in params:
            if "a" in param:
                values.append([int(value) for value in param.split(".")[1:]])

        # Put extracted values in ELM Dataframe
        for index, value in enumerate(values):
            elm.loc[index] = value

        return elm

    def __produce_specific_decay(self):

        thetaC = self.__kVars["phi"].copy()
        phiC = self.__kVars["theta"].copy()
        thetaC[thetaC<0] = thetaC[thetaC<0]+2*npy.pi

        decay = npy.empty([len(self.__elm), len(self.__kVars)], "c16")
        for index, wave in self.__elm.iterrows():

            decay[index] = scipy.special.sph_harm(wave["m"], wave["l"], thetaC, phiC)

        return decay

    def calculate(self, params):
        intensity = npy.zeros(len(self.__kVars), "c16")

        U11 = npy.zeros((2,len(self.__kVars)), "c16")
        U12 = npy.zeros((2,len(self.__kVars)), "c16")


        for wave1 in range(len(self.__elm)):

            Vs = self.__param_to_Vs(params, wave1)

            if self.__elm["e"][wave1] == 1:
                U11[0] += Vs * self.__decay[wave1]
                U12[0] += Vs * self.__decay[wave1].conjugate()
            if self.__elm["e"][wave1] == -1:
                U11[1] += Vs * self.__decay[wave1]
                U12[1] += Vs * self.__decay[wave1].conjugate()

        I0 = npy.real(U11[0]*U11[0].conjugate()+U12[0]*U12[0].conjugate()+U11[1]*U11[1].conjugate()+U12[1]*U12[1].conjugate())
        I1 = 2*(-npy.real(U11[0]*U12[0].conjugate()) + npy.real(U11[1]*U12[1].conjugate()))
        I2 = 2*(-npy.imag(U11[0]*U12[0].conjugate()) + npy.imag(U11[1]*U12[1].conjugate()))


        intensity = I0 - self.__kVars["pol"] * I1 * npy.cos(2*self.__kVars["alpha"])
        intensity -= self.__kVars["pol"] * I2 * npy.sin(2*self.__kVars["alpha"])

        # Kill's the intensity if there is still imaginary values left, and should display
        # those imaginary values
        if npy.sum(npy.imag(intensity)) > 1.e-6:
            print("Results are wrong! Imaginary values have been found!")

        self.error = intensity

        return npy.real(intensity)


#    def _spin_density(self):
#
#        npy.empty((2,2),dtype='c16')
#        rho[0][0] = npy.complex(1-self.__kVars["pol"]*npy.cos(2*self.__kVars["alpha"],0.)
#        rho[0][1] = npy.complex(0.,-1. * self.__kVars["pol"]*npy.sin(2 * self.__kVars["alpha"]))
#       rho[1][0] = npy.complex(0,self.__kVars["pol"] * npy.sin(2 * self.__kVars["alpha"]))
#       rho[1][1] = npy.complex(1 + self.__kVars["pol"] * npy.cos(2 * self.__kVars["alpha"]),0.)

#        return 0.5*rho

    def calculate_wave(self, params, wave_num):
        intensity = npy.zeros(len(self.__kVars), "c16")
        rho = npy.empty(len(self.__kVars), "c16")
        wave1 = wave_num

        U11 = npy.zeros((2,len(self.__kVars)), "c16")
        U12 = npy.zeros((2,len(self.__kVars)), "c16")


#        Vs = self.__param_to_Vs(params, wave1, wave1)
        a_string = f"a.{self.__elm['e'][wave1]}.{self.__elm['l'][wave1]}.{self.__elm['m'][wave1]}"
        p_string = f"p.{self.__elm['e'][wave1]}.{self.__elm['l'][wave1]}.{self.__elm['m'][wave1]}"
        Vs = npy.complex(params[a_string]*npy.cos(params[p_string]), params[a_string]*npy.sin(params[p_string]))


        if self.__elm["e"][wave1] == 1:
            U11[0] += Vs * self.__decay[wave1]
            U12[0] += Vs * self.__decay[wave1].conjugate()
        if self.__elm["e"][wave1] == -1:
            U11[1] += Vs * self.__decay[wave1]
            U12[1] += Vs * self.__decay[wave1].conjugate()

        I0 = npy.real(U11[0]*U11[0].conjugate()+U12[0]*U12[0].conjugate()+U11[1]*U11[1].conjugate()+U12[1]*U12[1].conjugate())
        I1 = 2*(-npy.real(U11[0]*U12[0].conjugate()) + npy.real(U11[1]*U12[1].conjugate()))
        I2 = 2*(-npy.imag(U11[0]*U12[0].conjugate()) + npy.imag(U11[1]*U12[1].conjugate()))


        intensity = I0 - self.__kVars["pol"] * I1 * npy.cos(2*self.__kVars["alpha"])
        intensity -= self.__kVars["pol"] * I2 * npy.sin(2*self.__kVars["alpha"])

        # Kill's the intensity if there is still imaginary values left, and should display
        # those imaginary values
        if npy.sum(npy.imag(intensity)) != 0:
            print("Results are wrong! Imaginary values have been found!")

        self.error = intensity

        return npy.real(intensity)

    def __param_to_Vs(self, params, wave1):
        value = npy.empty(1, "c16")

        # value[0] == wave1; value[1] == wave2

        a_string = f"a.{self.__elm['e'][wave1]}.{self.__elm['l'][wave1]}.{self.__elm['m'][wave1]}"
        p_string = f"p.{self.__elm['e'][wave1]}.{self.__elm['l'][wave1]}.{self.__elm['m'][wave1]}"
        value = npy.complex(params[a_string]*npy.cos(params[p_string]), params[a_string]*npy.sin(params[p_string]))

        return value

    def Phasediff(self, params, wave1, wave2):
        value = npy.empty(2, "c16")

        # value[0] == wave1; value[1] == wave2
        for index, i in enumerate([wave1, wave2]):
            a_string = f"a.{self.__elm['e'][i]}.{self.__elm['l'][i]}.{self.__elm['m'][i]}"
            p_string = f"p.{self.__elm['e'][i]}.{self.__elm['l'][i]}.{self.__elm['m'][i]}"
            value[index] = npy.complex(params[a_string]*npy.cos(params[p_string]), params[a_string]*npy.sin(params[p_string]))
        phasediff = npy.arctan(npy.imag(value[0]*value[1].conjugate())/npy.real(value[0]*value[1].conjugate()))

        return phasediff

# Calculate some moments from theproduction amplitudes
# also calculate asymmetries defined in the JPAC paper

    def calculate_moments_JPAC(self, params):
        A = npy.empty(9,'c16')
        S0 = P0 = P1 = D0 = D1 = D2 = complex(0,0)
        rat = rat2 = 0.
        sigma4 = sigmay = 0.

        for wave1 in range(len(self.__elm)):
            A[wave1] = self.__param_to_Vs(params, wave1)
        S0 = A[0]
        P0 = A[1]
        P1 = A[2]
        D0 = A[3]
        D1 = A[4]
        D2 = A[5]


        H100 = ne.evaluate("2.*(abs(S0)**2+abs(P0)**2+abs(D0)**2)")
        H000 = ne.evaluate("H100+2.*(abs(P1)**2+abs(D1)**2+abs(D2)**2)")

        H110 = ne.evaluate("(8./sqrt(15))*real(P0*conj(D0))+(4./sqrt(3.))*real(S0*conj(P0))")
        H010 = ne.evaluate("H110+(4/sqrt(5.))*real(P1*conj(D1))")

        H111 = ne.evaluate("(2./sqrt(5.))*real(P0*conj(D1))-(2./sqrt(15.))*real(P1*conj(D0))+(2./sqrt(3.))*real(S0*conj(P1))")
        H011 = ne.evaluate("H111+(2.*sqrt(2./5.))*real(P1*conj(D2))")

        H120 = ne.evaluate("(4./5.)*abs(P0)**2+(4./7.)*abs(D0)**2+(4./sqrt(5.))*real(S0*conj(D0))")
        H020 = ne.evaluate("H120-(2./5.)*abs(P1)**2+(2./7.)*abs(D1)**2-(4./7.)*abs(D2)**2")

        H121 = ne.evaluate("(2./sqrt(5.))*real(S0*conj(D1))+(2.*sqrt(3)/5.)*real(P0*conj(P1))+(2./7.)*real(D0*conj(D1))")
        H021 = ne.evaluate("H121+(2./7.)*sqrt(6.)*real(D1*conj(D2))")

        H022 = ne.evaluate("(2./sqrt(5))*real(S0*conj(D2))-(4./7.)*real(D0*conj(D2))")
        H122 = ne.evaluate("H022+(sqrt(6.)/7.)*abs(D1)**2+(sqrt(6.)/5.)*abs(P1)**2")

        rat = ne.evaluate("(abs(S0)**2+abs(P0)**2+abs(D0)**2)/(abs(P1)**2+abs(D1)**2+abs(D2)**2)")
        sigma4 = rat/(1+rat)

        rat2=ne.evaluate("(2./3.)*abs(S0)**2+(5./6.)*abs(D0)**2+(5./4.)*abs(D2)**2-(2.*sqrt(5.)/3.)*real(S0*conj(D0))-(sqrt(10./3))*real(S0*conj(D2))+(5./sqrt(6.))*real(D0*conj(D2))")
        sigmay = ne.evaluate("(rat2-abs(P1)**2)/(rat2+abs(P1)**2)")

        return H000,H010,H011,H020,H021,H022,H100,H110,H111,H120,H121,H122,sigma4,sigmay
