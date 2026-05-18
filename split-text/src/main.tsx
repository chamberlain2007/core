import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { Demo } from "./demo";

const root = document.getElementById("root");
if (root) {
  createRoot(root).render(
    <StrictMode>
      <Demo />
    </StrictMode>,
  );
}
