import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import axios from "axios";

function CryptoDetail() {
  const { symbol } = useParams();
  const [crypto, setCrypto] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    axios
      .get(`${import.meta.env.VITE_API_BASE_URL}/api/crypto/`)
      .then((res) => {
        console.log("✅ Full API response:", res.data);
        const cryptoList = res.data.results;
        const found = cryptoList.find(
          (c) => c.symbol.toUpperCase() === symbol.toUpperCase()
        );
        console.log("🔍 Found crypto:", found);
        setCrypto(found);
        setLoading(false);
      })
      .catch((err) => {
        console.error("❌ API error:", err);
        setLoading(false);
      });
  }, [symbol]);

  if (loading) return <div>Loading...</div>;
if (!crypto) return <p style={{ textAlign: 'center' }}>🔄 Loading crypto details...</p>;

  return (
 <div style={{
  maxWidth: '400px',
  margin: '2rem auto',
  padding: '1.5rem',
  border: '1px solid #ccc',
  borderRadius: '10px',
  boxShadow: '0 4px 8px rgba(0,0,0,0.1)',
  fontFamily: 'Arial, sans-serif',
}}>
  <h2 style={{ textAlign: 'center', color: '#333' }}>{crypto.symbol}</h2>
  <p><strong>Price:</strong> ${crypto.price}</p>
  <p><strong>24h Volume:</strong> ${crypto.volume_24h.toLocaleString()}</p>
   <p>
  <strong>24h Change:</strong>
  <span style={{ color: crypto.change_percent_24h < 0 ? 'red' : 'green' }}>
    {crypto.change_percent_24h < 0 ? ' 🔻' : ' 🔺'} {crypto.change_percent_24h}%
  </span>
</p>

  <p><strong>24h Change:</strong> <span style={{ color: crypto.change_percent_24h < 0 ? 'red' : 'green' }}>{crypto.change_percent_24h}%</span></p>
 </div>

);

}

export default CryptoDetail;
