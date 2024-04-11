import ProductDetail from '../components/Product';
import {render, waitFor, screen} from "@testing-library/react";
import {expect} from "chai";
import {vi} from 'vitest';
import {getUser, login} from "../api/users.api.jsx";
import {saveProduct} from "../api/products.api.jsx";
import {AuthProvider} from "../context/AuthContext.jsx";
import {MemoryRouter} from "react-router-dom";

let messages = {
    token: {
        user: 'test1Frontend',
        password: 'test1Frontend'
    },
    labels: {
        title: 'Detalles del producto'
    }
}

describe('Test products details', () => {

    const jsdomAlert = window.alert;
    window.alert = () => {
    };
    let token = undefined;
    let user = undefined;

    beforeEach(async () => {
        localStorage.removeItem('token')

        token = (await (await login(messages.token.user, messages.token.user)).json()).token;

        user = await (await getUser(12)).json();
        localStorage.setItem('token', token);
    });

    function loadRender() {
        return render(
            <MemoryRouter>
                <AuthProvider>
                    <ProductDetail/>
                </AuthProvider>
            </MemoryRouter>
        );
    }


    describe('OK Product Details', () => {

        test('Normal', async () => {
            /* ARRANGE */
            const product = {
                description: "Diseño para impresión 3D de una gallina. Está pensado para la diversión y el juego de los más pequeños. Los colores son los mostrados en la foto. Se puede ajustar al tamaño que se desee.",
                id: 9,
                imageRoute: "design_gallina.jpg",
                image_url: null,
                name: "Diseño gallina",
                price: "3.00",
                product_type: "D",
                seller: user.id,
                stock_quantity: 21
            };

            mockFetch(product);

            /* ACT */
            const {container} = loadRender();

            await waitFor(() => {
                expect(screen.getByText(messages.labels.title)).to.exist;
            });

            /* ASSERT */
            assertOKProductDetails(product, user, container);
        });

        test('Product with Oriental Characters', async () => {
            /* ARRANGE */
            const product = {
                description: "3D印刷のデザイン。子供たちの遊びと楽しみのために考案されました。写真に表示されている色です。サイズを調整できます。",
                id: 9,
                imageRoute: "oriental_design.jpg",
                image_url: null,
                name: "東方デザイン",
                price: "10.00",
                product_type: "O",
                seller: user.id,
                stock_quantity: 5
            };

            await saveProduct(product);

            mockFetch(product);

            /* ACT */
            const {container} = loadRender();

            await waitFor(() => {
                expect(screen.getByText(messages.labels.title)).to.exist;
            });

            /* ASSERT */
            assertOKProductDetails(product, user, container);
        });

        test('Product with Extreme Price', async () => {
            /* ARRANGE */
            const product = {
                description: "Product with Extreme Price",
                id: 9,
                imageRoute: "extreme_price.jpg",
                image_url: null,
                name: "High Price Product",
                price: "999999.99", // Extremely high price
                product_type: "E",
                seller: user.id,
                stock_quantity: 20
            };

            await saveProduct(product);

            mockFetch(product);

            /* ACT */
            const {container} = loadRender();

            await waitFor(() => {
                expect(screen.getByText(messages.labels.title)).to.exist;
            });

            /* ASSERT */
            assertOKProductDetails(product, user, container);
        });
    });
    describe("Injection Product Details", () => {
        test('Product with JavaScript Injection', async () => {
            /* ARRANGE */
            const product = {
                description: "<script>alert('JavaScript Injection');</script>",
                id: "9",
                imageRoute: "javascript_injection.jpg",
                image_url: "null",
                name: "Product with JS Injection",
                price: "15.00",
                product_type: "J",
                seller: "10",
                stock_quantity: "3"
            };

            mockFetch(product);

            /* ACT */
            const {container} = loadRender();

            await waitFor(() => {
                expect(screen.getByText("Detalles del producto")).to.exist;
            });

            /* ASSERT */
            assertInjectionProductDetails(product, user, container);
        });

        test('Product with HTML Injection', async () => {
            /* ARRANGE */
            const product = {
                description: "<div style='color:red;'>HTML Injection</div>",
                id: "9",
                imageRoute: "html_injection.jpg",
                image_url: "null",
                name: "Product with HTML Injection",
                price: "20.00",
                product_type: "H",
                seller: user.id,
                stock_quantity: "4"
            };

            mockFetch(product);

            /* ACT */
            const {container} = loadRender();

            await waitFor(() => {
                expect(screen.getByText(messages.labels.title)).to.exist;
            });

            /* ASSERT */
            assertInjectionProductDetails(product, user, container);
        });

        test('Product with SQL Injection', async () => {
            /* ARRANGE */
            const product = {
                description: "Product with SQL Injection DESCRIPTION; DROP TABLE Products;",
                id: "9; DROP TABLE Products;",
                imageRoute: "sql_injection.jpg",
                image_url: "null",
                name: "Product with SQL Injection NAME; DROP TABLE Products;",
                price: "25.00",
                product_type: "S",
                seller: user.id,
                stock_quantity: "6"
            };

            mockFetch(product);

            /* ACT */
            const {container} = loadRender();

            await waitFor(() => {
                expect(screen.getByText(messages.labels.title)).to.exist;
            });

            /* ASSERT */
            assertInjectionProductDetails(product, user, container);
        });
    });
});


// Auxiliar functions
function assertOKProductDetails(product, seller, container) {
    const checkProduct = ["description", "name", "price"];

    for (let i = 0; i < checkProduct.length; i++) {
        const expectedText = new RegExp(product[checkProduct[i]]);
        expect(screen.getByText(expectedText)).to.exist;
    }

    const productImgElement = container.querySelector('#product-img');
    expect(screen.getByAltText(product.name)).to.exist;

    const checkSeller = ["username"];

    for (let i = 0; i < checkSeller.length; i++) {
        const expectedText = new RegExp(seller[checkSeller[i]]);
        expect(screen.getByText(expectedText)).to.exist;
    }
}

function assertInjectionProductDetails(product, seller, container) {
    const checkProduct = ["description", "name", "price"];

    for (let i = 0; i < checkProduct.length; i++) {
        const expectedText = parseScriptAndHtml(product[checkProduct[i]]);
        expect(() => screen.queryByText(expectedText)).to.exist;
    }

    const productImgElement = container.querySelector('#product-img');
    expect(() => screen.queryByAltText(parseScriptAndHtml(product.name))).to.exist;

    const checkSeller = ["username"];

    for (let i = 0; i < checkSeller.length; i++) {
        const expectedText = parseScriptAndHtml(seller[checkSeller[i]]);
        expect(() => screen.queryByText(expectedText)).to.exist;
    }
}


function mockFetch(object) {
    vi.spyOn(window, 'fetch').mockImplementationOnce(() => {
        return Promise.resolve({
            json: () => Promise.resolve(object),
        });
    });
}

function parseScriptAndHtml(input) {
    // Conservar ciertos caracteres especiales y escapar otros
    const sanitizedInput = input.replace(/[<>"&'`]/g, function (match) {
        const escapeMap = {
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            '&': '&amp;',
            "'": '&#39;',
            '`': '&#x60;'
        };
        return escapeMap[match];
    });

    return sanitizedInput;
}






