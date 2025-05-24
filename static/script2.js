async function fetchTweets() {
    const response = await fetch('/api/tweets');
    const tweets = await response.json();

    const sentimentCounts = {
        Negative: 0,
        Neutral: 0,
        Positive: 0
    };

    let tweetsHTML = '';

    tweets.forEach(tweet => {
        tweetsHTML += `<p>${tweet.text}</p>`;
        sentimentCounts.Negative += tweet.sentiment.Negative;
        sentimentCounts.Neutral += tweet.sentiment.Neutral;
        sentimentCounts.Positive += tweet.sentiment.Positive;
    });

    document.getElementById('tweets').innerHTML = tweetsHTML;

    return sentimentCounts;
}

async function renderChart() {
    const sentimentCounts = await fetchTweets();

    const ctx = document.getElementById('sentimentChart').getContext('2d');
    const myChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Negative', 'Neutral', 'Positive'],
            datasets: [{
                label: 'Sentiment Scores',
                data: [sentimentCounts.Negative, sentimentCounts.Neutral, sentimentCounts.Positive],
                backgroundColor: [
                    'rgba(255, 99, 132, 0.2)',
                    'rgba(255, 206, 86, 0.2)',
                    'rgba(75, 192, 192, 0.2)'
                ],
                borderColor: [
                    'rgba(255, 99, 132, 1)',
                    'rgba(255, 206, 86, 1)',
                    'rgba(75, 192, 192, 1)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

document.addEventListener('DOMContentLoaded', renderChart);
