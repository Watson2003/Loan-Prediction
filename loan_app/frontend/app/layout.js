import './globals.css';

export const metadata = {
  title: 'Loan Approval Predictor',
  description: 'Enter loan details and receive an approval prediction from FastAPI.',
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
