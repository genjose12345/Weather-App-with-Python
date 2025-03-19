document.addEventListener('DOMContentLoaded', function() {
    console.log("DOM loaded - initializing weather app");
    
    // Initialize the autocomplete search
    setupAddressAutocomplete();
    
    // Add focus to the search input when the page loads
    const searchInput = document.querySelector('.search-container input');
    if (searchInput) {
        searchInput.focus();
    }
    
    // Country input formatting - force uppercase for country codes
    const countryInput = document.querySelector('input[name="country"]');
    if (countryInput) {
        countryInput.addEventListener('input', function() {
            this.value = this.value.toUpperCase();
            // Limit to 2 characters (standard country code)
            if (this.value.length > 2) {
                this.value = this.value.slice(0, 2);
            }
        });
    }
    
    // Auto-submit on pressing enter in any field
    const formInputs = document.querySelectorAll('.search-container input');
    formInputs.forEach(input => {
        input.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                document.querySelector('.search-container button').click();
            }
        });
    });
    
    // Add animation to the weather cards
    const cards = document.querySelectorAll('.weather-card');
    if (cards.length > 0) {
        cards.forEach((card, index) => {
            card.style.animation = `fadeIn 0.5s ease forwards ${index * 0.1}s`;
            card.style.opacity = '0';
        });
    }
    
    // Add animation to the forecast cards
    const forecastCards = document.querySelectorAll('.forecast-card');
    if (forecastCards.length > 0) {
        forecastCards.forEach((card, index) => {
            card.style.animation = `fadeInUp 0.5s ease forwards ${index * 0.1 + 0.3}s`;
            card.style.opacity = '0';
            card.style.transform = 'translateY(20px)';
        });
    }
    
    // Add dynamic background color based on temperature if available
    const tempElement = document.querySelector('.temperature');
    const mainCard = document.querySelector('.main-card');
    
    if (tempElement && mainCard) {
        const temp = parseInt(tempElement.textContent);
        let color;
        
        if (temp >= 90) {
            // Hot
            color = 'rgba(255, 152, 0, 0.1)';
        } else if (temp >= 70) {
            // Warm
            color = 'rgba(255, 193, 7, 0.1)';
        } else if (temp >= 50) {
            // Moderate
            color = 'rgba(139, 195, 74, 0.1)';
        } else if (temp >= 32) {
            // Cool
            color = 'rgba(3, 169, 244, 0.1)';
        } else {
            // Cold
            color = 'rgba(33, 150, 243, 0.1)';
        }
        
        mainCard.style.backgroundColor = color;
    }
    
    // Add subtle color to forecast cards based on max temperature
    forecastCards.forEach(card => {
        const maxTempElement = card.querySelector('.max-temp');
        if (maxTempElement) {
            const maxTemp = parseInt(maxTempElement.textContent);
            let color;
            
            if (maxTemp >= 90) {
                color = 'rgba(255, 152, 0, 0.08)';
            } else if (maxTemp >= 70) {
                color = 'rgba(255, 193, 7, 0.08)';
            } else if (maxTemp >= 50) {
                color = 'rgba(139, 195, 74, 0.08)';
            } else if (maxTemp >= 32) {
                color = 'rgba(3, 169, 244, 0.08)';
            } else {
                color = 'rgba(33, 150, 243, 0.08)';
            }
            
            card.style.backgroundImage = `linear-gradient(to bottom, white, ${color})`;
        }
    });
});

// Set up the main autocomplete search functionality
function setupAddressAutocomplete() {
    console.log("Setting up address autocomplete search");
    const searchInput = document.getElementById('location-search');
    const latField = document.getElementById('lat-field');
    const lngField = document.getElementById('lng-field');
    const form = document.getElementById('weather-form');
    
    if (!searchInput || !form) {
        console.error('Required form elements not found');
        return;
    }
    
    // Create a debounce function to limit API calls
    const debounce = (func, delay) => {
        let timeout;
        return function() {
            const context = this;
            const args = arguments;
            clearTimeout(timeout);
            timeout = setTimeout(() => func.apply(context, args), delay);
        };
    };
    
    // Create a container for autocomplete results
    const createAutocompleteContainer = () => {
        // Remove existing container if any
        const existingContainer = document.querySelector('.autocomplete-results');
        if (existingContainer) {
            existingContainer.remove();
        }
        
        // Create new container
        const container = document.createElement('div');
        container.className = 'autocomplete-results';
        
        // Position it below the search input
        const inputRect = searchInput.getBoundingClientRect();
        container.style.width = inputRect.width + 'px';
        container.style.top = (inputRect.bottom + window.scrollY) + 'px';
        container.style.left = (inputRect.left + window.scrollX) + 'px';
        
        document.body.appendChild(container);
        return container;
    };
    
    // Function to fetch address suggestions from our API
    const fetchAddressSuggestions = debounce(async (query) => {
        if (query.length < 2) {
            const container = document.querySelector('.autocomplete-results');
            if (container) {
                container.classList.remove('active');
                setTimeout(() => container.remove(), 300);
            }
            return;
        }
        
        try {
            // Fetch suggestions from our custom API endpoint
            const response = await fetch(`/address-autocomplete?q=${encodeURIComponent(query)}`);
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            
            const suggestions = await response.json();
            
            if (suggestions.length === 0) {
                const container = document.querySelector('.autocomplete-results');
                if (container) {
                    container.classList.remove('active');
                    setTimeout(() => container.remove(), 300);
                }
                return;
            }
            
            // Create or get container
            let container = document.querySelector('.autocomplete-results');
            if (!container) {
                container = createAutocompleteContainer();
            }
            
            // Clear existing results
            container.innerHTML = '';
            
            // Add each suggestion to the container
            suggestions.forEach(suggestion => {
                const item = document.createElement('div');
                item.className = 'autocomplete-item';
                
                // Highlight matching parts of the text
                const highlightedText = suggestion.text.replace(
                    new RegExp(query, 'gi'),
                    match => `<strong>${match}</strong>`
                );
                
                item.innerHTML = `
                    <i class="fas fa-map-marker-alt"></i>
                    <div class="location-text">
                        <div class="location-name">${highlightedText}</div>
                    </div>
                `;
                
                // Handle item selection
                item.addEventListener('click', function() {
                    searchInput.value = suggestion.text;
                    
                    // Set the coordinates in the hidden fields
                    if (latField && lngField) {
                        latField.value = suggestion.lat;
                        lngField.value = suggestion.lng;
                    }
                    
                    // Hide the autocomplete container
                    container.classList.remove('active');
                    setTimeout(() => container.remove(), 300);
                    
                    // Submit the form
                    form.submit();
                });
                
                container.appendChild(item);
            });
            
            // Show the container
            container.classList.add('active');
            
        } catch (error) {
            console.error('Error fetching address suggestions:', error);
            // Fallback to default form submission without autocomplete
        }
    }, 300); // 300ms debounce delay
    
    // Add input event listener to search input
    searchInput.addEventListener('input', function() {
        const query = this.value.trim();
        fetchAddressSuggestions(query);
    });
    
    // Hide autocomplete when clicking outside
    document.addEventListener('click', function(e) {
        if (!searchInput.contains(e.target)) {
            const container = document.querySelector('.autocomplete-results');
            if (container) {
                container.classList.remove('active');
                setTimeout(() => container.remove(), 300);
            }
        }
    });
    
    // Handle form submission
    form.addEventListener('submit', function(e) {
        console.log('Submitting form with location:', searchInput.value);
        return true; // Allow form submission
    });
    
    // Add CSS for autocomplete
    const style = document.createElement('style');
    style.textContent = `
        .autocomplete-results {
            position: absolute;
            background: white;
            border-radius: 8px;
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
            max-height: 300px;
            overflow-y: auto;
            z-index: 1000;
            opacity: 0;
            transform: translateY(-10px);
            transition: opacity 0.2s ease, transform 0.2s ease;
            display: none;
        }
        
        .autocomplete-results.active {
            opacity: 1;
            transform: translateY(0);
            display: block;
        }
        
        .autocomplete-item {
            padding: 12px 15px;
            display: flex;
            align-items: center;
            cursor: pointer;
            border-bottom: 1px solid rgba(0, 0, 0, 0.05);
            transition: background-color 0.2s ease;
        }
        
        .autocomplete-item:last-child {
            border-bottom: none;
        }
        
        .autocomplete-item:hover {
            background-color: rgba(74, 111, 165, 0.1);
        }
        
        .autocomplete-item i {
            margin-right: 12px;
            color: #4a6fa5;
            font-size: 16px;
        }
        
        .autocomplete-item .location-name {
            font-size: 14px;
            color: #333;
        }
        
        .autocomplete-item strong {
            color: #4a6fa5;
            font-weight: 600;
        }
    `;
    document.head.appendChild(style);
}

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
@keyframes fadeIn {
    from {
        opacity: 0;
        transform: translateY(10px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

/* Improved styling for Google Places Autocomplete dropdown */
.pac-container {
    border-radius: 12px;
    margin-top: 5px;
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.2);
    font-family: 'Poppins', sans-serif;
    border: none;
    z-index: 9999 !important;
    overflow: hidden;
}

.pac-item {
    padding: 12px 15px;
    cursor: pointer;
    border-top: 1px solid rgba(0, 0, 0, 0.05);
    transition: background-color 0.2s ease;
}

.pac-item:first-child {
    border-top: none;
}

.pac-item:hover {
    background-color: rgba(74, 111, 165, 0.1);
}

.pac-item-selected {
    background-color: rgba(74, 111, 165, 0.15);
}

.pac-icon {
    margin-right: 10px;
}

.pac-item-query {
    font-size: 15px;
    font-weight: 500;
    color: #166088;
}

.pac-matched {
    font-weight: 700;
    color: #4a6fa5;
}

.pac-item-query + span {
    font-size: 13px;
    color: #666;
    margin-left: 4px;
}

.highlight-error {
    animation: shake 0.5s cubic-bezier(.36,.07,.19,.97) both;
    border-color: #ff3860 !important;
    box-shadow: 0 0 0 3px rgba(255, 56, 96, 0.2) !important;
}

@keyframes shake {
    10%, 90% { transform: translate3d(-1px, 0, 0); }
    20%, 80% { transform: translate3d(2px, 0, 0); }
    30%, 50%, 70% { transform: translate3d(-3px, 0, 0); }
    40%, 60% { transform: translate3d(3px, 0, 0); }
}
`;
document.head.appendChild(style); 