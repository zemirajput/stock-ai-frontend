import { Routes, Route } from "react-router-dom";

import MainLayout from "./layouts/MainLayout";

import Dashboard from "./pages/Dashboard";
import Prediction from "./pages/Prediction";
import Analytics from "./pages/Analytics";
import About from "./pages/About";

function App() {

  return (

    <Routes>

      <Route element={<MainLayout />}>

        <Route
          path="/"
          element={<Dashboard />}
        />

        <Route
          path="/prediction"
          element={<Prediction />}
        />
        <Route
          path="/analytics"
          element={<Analytics />}
        />

        <Route
          path="/about"
          element={<About />}
         />

      </Route>

    </Routes>

  );

}

export default App;