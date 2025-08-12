Below is a detailed implementation plan using proper markdown. This plan outlines every change—including new files and modifications—to build the “Kenia e Key” website that monitors the cheapest flight tickets across all Brazilian airports using mock data.

---

### 1. Create Utility Files for Data

**a. Create Airport List File**  
_File: src/lib/airports.ts_  
- Purpose: Define an array with objects for major Brazilian airports (using IATA codes and names).  
- Error Handling: Validate that the list is not empty before using it in dropdowns.  

_Example Code:_  
```typescript
export interface Airport {
  code: string;
  name: string;
}

export const airports: Airport[] = [
  { code: "GRU", name: "São Paulo/Guarulhos International Airport" },
  { code: "GIG", name: "Rio de Janeiro/Galeão International Airport" },
  { code: "BSB", name: "Brasília International Airport" },
  { code: "CNF", name: "Confins International Airport, Belo Horizonte" },
  { code: "SSA", name: "Deputado Luís Eduardo Magalhães International Airport, Salvador" },
  // Add additional major Brazilian airports as needed.
];
```

**b. Create Mock Flight Data File**  
_File: src/lib/mockFlights.ts_  
- Purpose: Provide an array of flight objects including departure, arrival, times, price, airline, and flight number.  
- Best Practices: Use TypeScript interfaces and include explanatory comments.  
- Error Handling: Ensure the data can be filtered; if empty, return a proper “no flights found” message.  

_Example Code:_  
```typescript
export interface Flight {
  id: string;
  departureAirport: string;
  arrivalAirport: string;
  departureTime: string;
  arrivalTime: string;
  price: number;
  airline: string;
  flightNumber: string;
}

export const mockFlights: Flight[] = [
  {
    id: "1",
    departureAirport: "GRU",
    arrivalAirport: "GIG",
    departureTime: "2023-10-12T08:00:00Z",
    arrivalTime: "2023-10-12T09:00:00Z",
    price: 350.00,
    airline: "LATAM",
    flightNumber: "LA123"
  },
  {
    id: "2",
    departureAirport: "BSB",
    arrivalAirport: "SSA",
    departureTime: "2023-10-13T10:00:00Z",
    arrivalTime: "2023-10-13T12:00:00Z",
    price: 280.00,
    airline: "GOL",
    flightNumber: "G3123"
  },
  // Add more flight data as needed.
];
```

---

### 2. Create API Endpoint for Flight Search

**File: src/app/api/flights/route.ts**  
- Purpose: Simulate flight search using query parameters (origin, destination, date) and return relevant mock flight data.  
- Steps:  
  - Use the Next.js App Router with GET method.  
  - Read URL search parameters and filter the flights accordingly.  
  - Include error handling (e.g., missing parameters) with 400 response and try/catch for any internal errors.  

_Example Code:_  
```typescript
import { NextResponse } from "next/server";
import { mockFlights, Flight } from "../../../lib/mockFlights";

export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    const origin = searchParams.get("origin");
    const destination = searchParams.get("destination");
    const date = searchParams.get("date");

    if (!origin || !destination || !date) {
      return NextResponse.json({ error: "Parâmetros ausentes." }, { status: 400 });
    }

    // Filter flights based on search – this is a simple example:
    const filteredFlights: Flight[] = mockFlights.filter(flight => 
      flight.departureAirport === origin && flight.arrivalAirport === destination &&
      flight.departureTime.startsWith(date)
    );

    return NextResponse.json({ flights: filteredFlights });
  } catch (error) {
    return NextResponse.json({ error: "Erro interno, tente novamente." }, { status: 500 });
  }
}
```

---

### 3. Create UI Components

**a. Flight Search Form Component**  
_File: src/components/FlightSearchForm.tsx_  
- Purpose: Present a modern, clean form for users to select departure, destination (using dropdowns from our airports file), and a date input.  
- Functionality:  
  - Validate that all fields are selected.  
  - On submit, trigger a callback to fetch flight results.  
- UI Considerations: Use simple typography, clear spacing, and modern form inputs.  
- Error Handling: Display inline errors for missing fields.

_Example Code:_  
```tsx
"use client";

import { useState } from "react";
import { airports } from "../lib/airports";

interface FlightSearchFormProps {
  onSearch: (data: { origin: string; destination: string; date: string }) => void;
}

export default function FlightSearchForm({ onSearch }: FlightSearchFormProps) {
  const [origin, setOrigin] = useState("");
  const [destination, setDestination] = useState("");
  const [date, setDate] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!origin || !destination || !date) {
      setError("Por favor, preencha todos os campos.");
      return;
    }
    setError("");
    onSearch({ origin, destination, date });
  };

  return (
    <form onSubmit={handleSubmit} className="max-w-md mx-auto p-4 bg-white rounded shadow">
      <h2 className="text-2xl mb-4 text-center">Buscar Passagens</h2>
      {error && <p className="text-red-500 mb-2">{error}</p>}
      <div className="mb-4">
        <label className="block text-sm font-medium">Origem</label>
        <select 
          value={origin} 
          onChange={(e) => setOrigin(e.target.value)} 
          className="w-full border border-gray-300 p-2 rounded"
        >
          <option value="">Selecione um aeroporto</option>
          {airports.map((airport) => (
            <option key={airport.code} value={airport.code}>
              {airport.name} ({airport.code})
            </option>
          ))}
        </select>
      </div>
      <div className="mb-4">
        <label className="block text-sm font-medium">Destino</label>
        <select 
          value={destination} 
          onChange={(e) => setDestination(e.target.value)} 
          className="w-full border border-gray-300 p-2 rounded"
        >
          <option value="">Selecione um aeroporto</option>
          {airports.map((airport) => (
            <option key={airport.code} value={airport.code}>
              {airport.name} ({airport.code})
            </option>
          ))}
        </select>
      </div>
      <div className="mb-4">
        <label className="block text-sm font-medium">Data de Partida</label>
        <input 
          type="date" 
          value={date} 
          onChange={(e) => setDate(e.target.value)} 
          className="w-full border border-gray-300 p-2 rounded"
        />
      </div>
      <button type="submit" className="w-full bg-blue-600 text-white p-2 rounded hover:bg-blue-700">
        Buscar
      </button>
    </form>
  );
}
```

**b. Flight List Component**  
_File: src/components/FlightList.tsx_  
- Purpose: Render a list of flight cards that include key details (departure/arrival info, dates, price, airline).  
- UI Considerations: Modern card layout with clear typography, color-highlighted price, and ample spacing.  
- Error Handling: Show a friendly message if no flights are found.

_Example Code:_  
```tsx
"use client";

import { Flight } from "../lib/mockFlights";

interface FlightListProps {
  flights: Flight[];
}

export default function FlightList({ flights }: FlightListProps) {
  if (flights.length === 0) {
    return <p className="text-center text-gray-600 mt-4">Nenhuma passagem encontrada.</p>;
  }

  return (
    <div className="max-w-4xl mx-auto mt-6">
      {flights.map((flight) => (
        <div key={flight.id} className="border p-4 rounded shadow mb-4">
          <h3 className="text-xl font-semibold mb-1">
            {flight.airline} - {flight.flightNumber}
          </h3>
          <p>
            De {flight.departureAirport} para {flight.arrivalAirport}
          </p>
          <p>
            Partida: {new Date(flight.departureTime).toLocaleString()} | Chegada:{" "}
            {new Date(flight.arrivalTime).toLocaleString()}
          </p>
          <p className="text-blue-700 font-bold mt-2">Preço: R$ {flight.price.toFixed(2)}</p>
        </div>
      ))}
    </div>
  );
}
```

---

### 4. Home Page Integration

**File: src/app/page.tsx**  
- Purpose: Serve as the landing page for “Kenia e Key” with a hero section and the integrated flight search form and results list.  
- Steps:  
  - Import the FlightSearchForm and FlightList components.  
  - Manage state variables for flight results, loading status, and error messages.  
  - Call the API endpoint asynchronously (using fetch) when the form is submitted.  
  - Display proper messages when loading or if an error occurs.  
- UI/UX: Clean hero with title/subtitle and modern layout; responsive design for mobile and desktop.

_Example Code:_  
```tsx
"use client";

import { useState } from "react";
import FlightSearchForm from "../components/FlightSearchForm";
import FlightList from "../components/FlightList";
import { Flight } from "../lib/mockFlights";

export default function Home() {
  const [flights, setFlights] = useState<Flight[]>([]);
  const [loading, setLoading] = useState(false);
  const [apiError, setApiError] = useState("");

  const handleSearch = async (searchData: { origin: string; destination: string; date: string }) => {
    setLoading(true);
    setApiError("");
    try {
      const query = new URLSearchParams(searchData).toString();
      const res = await fetch(`/api/flights?${query}`);
      const data = await res.json();
      if (res.ok) {
        setFlights(data.flights);
      } else {
        setApiError(data.error || "Erro desconhecido.");
      }
    } catch (error) {
      setApiError("Erro ao conectar com o servidor.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-gray-100 p-4">
      <section className="text-center mb-8">
        <h1 className="text-4xl font-bold mb-4">Kenia e Key</h1>
        <p className="text-lg text-gray-700">
          Monitoramento de passagens aéreas mais baratas no Brasil
        </p>
      </section>
      <FlightSearchForm onSearch={handleSearch} />
      {loading && <p className="text-center mt-4">Carregando...</p>}
      {apiError && <p className="text-center text-red-500 mt-4">{apiError}</p>}
      <FlightList flights={flights} />
    </main>
  );
}
```

---

### 5. Styling Enhancements

**File: src/app/globals.css**  
- Purpose: Apply modern UI styles—clear typography, spacing, and a professional color palette.  
- Changes:  
  - Add CSS classes for card shadows, rounded corners, and form styling if not already defined.  
  - Use a consistent color scheme (for example, blue for primary actions and soft gray for backgrounds).  

_Sample Additions:_  
```css
/* globals.css additional custom styles */
body {
  font-family: sans-serif;
  background-color: #f7fafc;
}
```

---

### 6. Testing and Best Practices

- Use try/catch blocks in API endpoints for robust error handling.  
- Validate input on the search form to prevent empty submissions.  
- Test the API endpoint using curl commands such as:  
  curl -G "http://localhost:3000/api/flights" --data-urlencode "origin=GRU" --data-urlencode "destination=GIG" --data-urlencode "date=2023-10-12"  
- Ensure state management in the home page correctly handles loading and error conditions.  
- Adhere to Next.js best practices with functional components and dynamic import if needed.

---

### Summary

- Created utility files (airports.ts and mockFlights.ts) to centralize data.  
- Developed an API endpoint (src/app/api/flights/route.ts) that filters mock flight data based on search parameters.  
- Built two key UI components: FlightSearchForm for input and FlightList for displaying flight details.  
- Integrated these components in the homepage (src/app/page.tsx) with state management and error handling.  
- Enhanced the UI with custom styles in globals.css using modern typography and spacing.  
- The overall plan supports real-world features including input validation, robust error management, and responsive design for monitoring airline passage pricing.
