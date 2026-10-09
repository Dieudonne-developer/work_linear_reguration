
import { useState } from "react";
import "./App.css";

// Do not add a trailing slash to the backend URL.
const API_URL = "https://work-linear-reguration.onrender.com";

function App() {
  const [studyHours, setStudyHours] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const analyzeStudent = async (event) => {
    event.preventDefault();

    if (studyHours.trim() === "") {
      setError("Please enter the number of study hours.");
      setResult(null);
      return;
    }

    const hours = Number(studyHours);

    if (!Number.isFinite(hours) || hours < 0) {
      setError("Please enter a valid number of study hours (0 or more).");
      setResult(null);
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    try {
      // Remove any trailing slash to prevent //api/analyze.
      const baseURL = API_URL.replace(/\/+$/, "");
      const endpoint = `${baseURL}/api/analyze`;

      const response = await fetch(endpoint, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          study_hours: hours,
        }),
      });

      const data = await response.json().catch(() => ({}));

      if (!response.ok) {
        const message =
          typeof data.detail === "string"
            ? data.detail
            : `Request failed with status ${response.status}.`;

        throw new Error(message);
      }

      setResult(data);
    } catch (err) {
      console.error("Analysis request failed:", err);

      setError(
        err.message ||
          "Could not connect to the backend. Please try again."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <header className="header">
        <h1>Correlation vs Linear Regression</h1>

        <p>
          Enter study hours to see how linear regression
          predicts a score while correlation describes the
          relationship in the dataset.
        </p>
      </header>

      <main className="container">
        {/* INPUT */}
        <section className="input-card">
          <h2>Student Input</h2>

          <form onSubmit={analyzeStudent}>
            <label htmlFor="studyHours">
              Enter Study Hours
            </label>

            <div className="input-row">
              <input
                id="studyHours"
                type="number"
                min="0"
                step="0.1"
                value={studyHours}
                onChange={(event) =>
                  setStudyHours(event.target.value)
                }
                placeholder="Example: 6"
                required
              />

              <button type="submit" disabled={loading}>
                {loading ? "Analyzing..." : "Analyze"}
              </button>
            </div>
          </form>

          {error && (
            <div className="error" role="alert">
              {error}
            </div>
          )}
        </section>

        {/* RESULTS */}
        {result && (
          <section className="results">
            {/* LINEAR REGRESSION */}
            <div className="result-card regression-card">
              <div className="card-label">
                LINEAR REGRESSION
              </div>

              <h2>Prediction</h2>

              <div className="input-result">
                <span>Study Hours</span>
                <strong>{result.study_hours} hours</strong>
              </div>

              <div className="prediction">
                <span>Predicted Exam Score</span>
                <strong>
                  {result.regression.predicted_score}
                  <small> / 100</small>
                </strong>
              </div>

              <div
                className={`pass-result ${
                  result.regression.result === "PASS"
                    ? "pass"
                    : "fail"
                }`}
              >
                {result.regression.result}
              </div>

              <p className="equation">
                {result.regression.equation}
              </p>

              <p className="description">
                Linear regression uses the entered study
                hours to predict a numerical exam score.
                The predicted score is then compared with
                the pass mark of{" "}
                <strong>{result.regression.pass_mark}</strong>.
              </p>
            </div>

            {/* CORRELATION */}
            <div className="result-card correlation-card">
              <div className="card-label">
                CORRELATION
              </div>

              <h2>Relationship</h2>

              <div className="correlation-value">
                <span>Pearson Correlation (r)</span>
                <strong>
                  {result.correlation.pearson_r}
                </strong>
              </div>

              <div className="relationship">
                {result.correlation.relationship}
              </div>

              <div className="p-value">
                p-value: {result.correlation.p_value}
              </div>

              <p className="description">
                Correlation is calculated from the{" "}
                <strong>entire dataset</strong>. It describes
                the strength and direction of the relationship
                between study hours and exam scores.
              </p>

              <div className="important-note">
                <strong>Important:</strong>

                <p>
                  Changing the study-hours input does{" "}
                  <strong>not change correlation</strong>.
                </p>

                <p>
                  Correlation does not predict an individual
                  student's score or PASS/FAIL result.
                </p>
              </div>
            </div>
          </section>
        )}

        {/* DIFFERENCE */}
        <section className="difference-card">
          <h2>The Difference</h2>

          <div className="difference-grid">
            <div>
              <h3>Correlation</h3>

              <p>
                Measures the strength and direction of the
                relationship between two variables using
                the dataset.
              </p>

              <div className="example">
                <strong>Output:</strong>
                <br />
                Pearson r = dataset result
                <br />
                Relationship strength and direction
              </div>
            </div>

            <div>
              <h3>Linear Regression</h3>

              <p>
                Uses study hours to predict a numerical
                exam score for an individual input.
              </p>

              <div className="example">
                <strong>Input:</strong>
                <br />
                Study Hours = your entered value
                <br />
                <br />
                <strong>Output:</strong>
                <br />
                Predicted Score
                <br />
                PASS / FAIL
              </div>
            </div>
          </div>
        </section>

        {/* SIMPLE EXPLANATION */}
        <section className="message-card">
          <h2>In Simple Terms</h2>

          <p>
            <strong>Correlation asks:</strong>
            <br />
            "Are study hours and exam scores related?"
          </p>

          <p>
            <strong>Linear regression asks:</strong>
            <br />
            "If this student studies this many hours,
            what score can we predict?"
          </p>
        </section>
      </main>

      <footer>
        Correlation vs Linear Regression Demo
      </footer>
    </div>
  );
}

export default App;
