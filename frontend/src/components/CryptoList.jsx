import React, { useEffect, useState } from "react";
import axios from "axios";
import { Link } from "react-router-dom";

const CryptoList = () => {
  const [cryptos, setCryptos] = useState([]);

  useEffect(() => {
    axios
      .get(`${import.meta.env.VITE_API_BASE_URL}/api/crypto/`)
      .then((res) => {
        console.log("✅ API raw response:", res.data);
        setCryptos(res.data.results); // ✅ Extract only the array
      })
      .catch((err) => {
        console.error("❌ API error:", err);
        setCryptos([]); // Optional: avoid crash on error
      });
  }, []);

  return (
    <div>
      <h2>Crypto Prices</h2>
      {cryptos.length === 0 ? (
        <p>No crypto data available</p>
      ) : (
        <ul>
          {cryptos.map((c) => (
            <li key={c.symbol}>
              <Link to={`/crypto/${c.symbol}`}>
                {c.name} ({c.symbol}) - ${c.price_usd}
              </Link>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default CryptoList;
