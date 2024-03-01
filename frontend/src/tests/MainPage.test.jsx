import { test } from 'vitest'
import { render, screen } from "@testing-library/react";
import MainPage from '../pages/MainPage'
import '@testing-library/jest-dom'
import { http } from 'msw';
import { setupServer } from 'msw/node';

const server = setupServer(
  http.get('/products/api/v1/products', (req, res, ctx) => {
    // Check if the request has the correct query parameter
    return res(
      ctx.status(200),
      ctx.json([
        { id: 1, name: 'Product 1', price: 100 },
        { id: 2, name: 'Product 2', price: 200 },
        // Add more products here...
      ])
    );

  })
);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());


test('renders MainPage without crashing', () => {
  render(<MainPage />)
})

test('contains expected texts', () => {
  render(<MainPage />)
  
  expect(screen.getByText('¡Explora la innovación en 3D!')).toBeInTheDocument()
  expect(screen.getByText('Encuentra diseños, impresoras y materiales de alta calidad.')).toBeInTheDocument()
  expect(screen.getByText('¡Haz tus ideas realidad!')).toBeInTheDocument()
  expect(screen.getByText('Diseños destacados')).toBeInTheDocument()
  expect(screen.getByText('Mejores artistas')).toBeInTheDocument()
  expect(screen.getByText('Impresoras a la venta')).toBeInTheDocument()
  expect(screen.getByText('Materiales a la venta')).toBeInTheDocument()

  const solicitarImpresionElement = screen.getByRole('button', { name: 'Solicitar impresión' });
  expect(solicitarImpresionElement).toBeInTheDocument();
})