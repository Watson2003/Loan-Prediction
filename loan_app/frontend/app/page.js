"use client";

import { useState } from "react";

const defaultValues = {
  Gender: "Male",
  Married: "No",
  Dependents: "0",
  Education: "Graduate",
  Self_Employed: "No",
  Property_Area: "Urban",
  Credit_History: "1",
  ApplicantIncome: "3000",
  CoapplicantIncome: "0",
  LoanAmount: "150",
  Loan_Amount_Term: "360",
};

const options = {
  Gender: ["Male", "Female"],
  Married: ["No", "Yes"],
  Dependents: ["0", "1", "2", "3+"],
  Education: ["Graduate", "Not Graduate"],
  Self_Employed: ["No", "Yes"],
  Property_Area: ["Rural", "Semiurban", "Urban"],
  Credit_History: ["0", "1"],
};

export default function Home() {
  const [formValues, setFormValues] = useState(defaultValues);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleChange = (event) => {
    const { name, value } = event.target;
    setFormValues((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setLoading(true);
    setError("");
    setMessage("");

    try {
      const response = await fetch("/api/predict", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(formValues),
      });

      const data = await response.json();
      if (data.error) {
        setError(data.error);
      } else {
        setMessage(
          `${data.decision}${data.probability ? ` (confidence ${Math.round(data.probability * 100)}%)` : ""}`
        );
      }
    } catch (exception) {
      setError("Unable to connect to the backend. Please try again later.");
    }

    setLoading(false);
  };

  return (
    <main className="container">
      <section className="card">
        <h1>Loan Approval Predictor</h1>
        <p>Fill out the loan details and get an instant approval prediction.</p>

        {error && <div className="alert alert-error">{error}</div>}
        {message && <div className="alert alert-success">{message}</div>}

        <form className="loan-form" onSubmit={handleSubmit}>
          {Object.entries(options).map(([key, values]) => (
            <label key={key}>
              {key.replace(/_/g, " ")}
              <select name={key} value={formValues[key]} onChange={handleChange}>
                {values.map((option) => (
                  <option key={option} value={option}>
                    {option}
                  </option>
                ))}
              </select>
            </label>
          ))}

          <label>
            Applicant Income
            <input
              type="number"
              name="ApplicantIncome"
              value={formValues.ApplicantIncome}
              onChange={handleChange}
              min="0"
              step="0.01"
              required
            />
          </label>

          <label>
            Coapplicant Income
            <input
              type="number"
              name="CoapplicantIncome"
              value={formValues.CoapplicantIncome}
              onChange={handleChange}
              min="0"
              step="0.01"
              required
            />
          </label>

          <label>
            Loan Amount
            <input
              type="number"
              name="LoanAmount"
              value={formValues.LoanAmount}
              onChange={handleChange}
              min="0"
              step="0.01"
              required
            />
          </label>

          <label>
            Loan Amount Term
            <input
              type="number"
              name="Loan_Amount_Term"
              value={formValues.Loan_Amount_Term}
              onChange={handleChange}
              min="1"
              required
            />
          </label>

          <button type="submit" className="button" disabled={loading}>
            {loading ? "Predicting…" : "Predict Loan Approval"}
          </button>
        </form>
      </section>
    </main>
  );
}
