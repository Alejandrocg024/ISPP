import {test} from 'vitest'
import {render, screen} from "@testing-library/react";
import MainPage from '../pages/MainPage'
import '@testing-library/jest-dom'
import {http} from 'msw';
import {setupServer} from 'msw/node';

const messages = {
    featuredDesignsMessage: 'Diseños destacados',
    topArtistsMessage: 'Mejores artistas',
    printersForSaleMessage: 'Impresoras a la venta',
    materialsForSaleMessage: 'Materiales a la venta',
    errorMessage: 'Error al obtener los productos'
};

describe('Test for MainPage', () => {

    beforeAll(() => server.listen());
    afterEach(() => server.resetHandlers());
    afterAll(() => server.close());

    test('renders MainPage without crashing', () => {
        render(<MainPage/>)
    })

    test('contains expected texts', () => {
        render(<MainPage />);

        expect(screen.getByText(messages.featuredDesignsMessage)).toBeInTheDocument();
        expect(screen.getByText(messages.topArtistsMessage)).toBeInTheDocument();
        expect(screen.getByText(messages.printersForSaleMessage)).toBeInTheDocument();
        expect(screen.getByText(messages.materialsForSaleMessage)).toBeInTheDocument();

        const requestPrintButtonElement = screen.getByRole('button', { name: messages.requestPrintButtonName });
        expect(requestPrintButtonElement).toBeInTheDocument();
    });
})

const server = setupServer(
    http.get('/products/api/v1/products', (req, res, ctx) => {
        // Check if the request has the correct query parameter
        if (req.url.searchParams.get('product_type')) {
            return res(
                ctx.status(200),
                ctx.json([
                    {id: 1, name: 'Product 1', price: 100},
                    {id: 2, name: 'Product 2', price: 200},
                    // Add more products here...
                ])
            );
        } else {
            return res(
                ctx.status(400),
                ctx.json({message: messages.errorMessage})
            );
        }
    })
);