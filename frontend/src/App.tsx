import { Route, Routes } from 'react-router-dom';

const Home = () => (
  <main className="min-h-screen bg-background text-foreground">
    <div className="container flex min-h-screen flex-col items-center justify-center gap-4 py-16">
      <h1 className="text-4xl font-semibold tracking-tight">HotelStaffIA</h1>
      <p className="text-muted-foreground">
        Sistema de gestión de staff con agente IA integrado.
      </p>
      <p className="text-sm text-muted-foreground">
        El frontend está en scaffolding. Las pantallas se implementan en el Ejercicio 3.
      </p>
    </div>
  </main>
);

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
    </Routes>
  );
}
