document.getElementById('stock-form').addEventListener('submit', function(event) {
    event.preventDefault();

    const symbol = document.getElementById('symbol').value;

    fetch(`/get_stock_info?symbol=${symbol}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                document.getElementById('stock-info').innerHTML = `<p>${data.error}</p>`;
            } else {
                document.getElementById('stock-info').innerHTML = `
                    <p><strong>Symbol:</strong> ${data.symbol}</p>
                    <p><strong>Price:</strong> ${data.price}</p>
                    <p><strong>Open:</strong> ${data.open}</p>
                    <p><strong>High:</strong> ${data.high}</p>
                    <p><strong>Low:</strong> ${data.low}</p>
                    <p><strong>Previous Close:</strong> ${data.prevClose}</p>
                `;
            }
        })
        .catch(error => {
            console.error('Error fetching stock info:', error);
            document.getElementById('stock-info').innerHTML = `<p>Error fetching stock info. Please try again later.</p>`;
        });
});
