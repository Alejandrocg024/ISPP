import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { expect } from 'chai';
import { vi } from 'vitest';
import UserDetail from '../components/User';
import { AuthProvider } from '../context/AuthContext.jsx';

let messages = {
    token: {
        user: 'test1Frontend',
        password: 'test1Frontend'
    },
    labels: {
        title: 'Detalles de usuario'
    }
};

describe("User Details", () => {

    function loadRender() {
        return render(
            <MemoryRouter>
                <AuthProvider>
                    <UserDetail />
                </AuthProvider>
            </MemoryRouter>
        );
    }

    describe("OK User Details", () => {
        test("Normal", async () => {
            /* ARRANGE */
            const user = {
                id: 10,
                address: "Avenida Reina Mercedes, 16, 4B",
                city: "Sevilla",
                email: "davidhernandez@gmail.com",
                first_name: "David",
                is_designer: false,
                is_printer: false,
                last_name: "Hernández de la Prada",
                postal_code: 41012
            };

            mockFetch(user);

            /* ACT */
            const { container } = loadRender();

            await waitFor(() => expect(screen.getByText(messages.labels.title)).to.exist);

            /* ASSERT */
            assertOKUserDetails(user, container);
        });

        test("User with Oriental Characters", async () => {
            /* ARRANGE */
            const user = {
                id: 10,
                address: "東京都中央区",
                city: "東京東京",
                email: "hanako@example.com",
                first_name: "花子花",
                is_designer: true,
                is_printer: false,
                last_name: "山田山田",
                postal_code: 100001
            };

            mockFetch(user);

            /* ACT */
            const { container } = loadRender();

            await waitFor(() => expect(screen.getByText(messages.labels.title)).to.exist);

            /* ASSERT */
            assertOKUserDetails(user, container);
        });

        test("User with Extreme Postal Code", async () => {
            /* ARRANGE */
            const user = {
                id: 10,
                address: "123 Main Street",
                city: "Cityville",
                email: "john.doe@example.com",
                first_name: "John",
                is_designer: false,
                is_printer: true,
                last_name: "Doe",
                postal_code: 999999 // Extremely high postal code
            };

            mockFetch(user);

            /* ACT */
            const { container } = loadRender();

            await waitFor(() => expect(screen.getByText(messages.labels.title)).to.exist);

            /* ASSERT */
            assertOKUserDetails(user, container);
        });
    });

    describe("Injection User Details", () => {
        test("User with JavaScript Injection", async () => {
            /* ARRANGE */
            const user = {
                id: 10,
                address: "<script>alert('JavaScript Injection');</script>",
                city: "Cityville",
                email: "john.doe@example.com",
                first_name: "John",
                is_designer: true,
                is_printer: true,
                last_name: "Doe",
                postal_code: 12345
            };

            mockFetch(user);

            /* ACT */
            const { container } = loadRender();

            await waitFor(() => expect(screen.getByText(messages.labels.title)).to.exist);

            /* ASSERT */
            assertInjectionUserDetails(user, container);
        });

        test("User with HTML Injection", async () => {
            /* ARRANGE */
            const user = {
                id: 10,
                address: "<div style='color:red;'>HTML Injection</div>",
                city: "Cityville",
                email: "john.doe@example.com",
                first_name: "John",
                is_designer: true,
                is_printer: true,
                last_name: "Doe",
                postal_code: 12345
            };

            mockFetch(user);

            /* ACT */
            const { container } = loadRender();

            await waitFor(() => expect(screen.getByText(messages.labels.title)).to.exist);

            /* ASSERT */
            assertInjectionUserDetails(user, container);
        });

        test("User with SQL Injection", async () => {
            /* ARRANGE */
            const user = {
                id: 10,
                address: "User with SQL Injection ADDRESS; DROP TABLE Users;",
                city: "Cityville",
                email: "john.doe@example.com",
                first_name: "User with SQL Injection NAME; DROP TABLE Users;",
                is_designer: true,
                is_printer: true,
                last_name: "Doe",
                postal_code: "User with SQL Injection POSTAL CODE; DROP TABLE Users;"
            };

            mockFetch(user);

            /* ACT */
            const { container } = loadRender();

            await waitFor(() => expect(screen.getByText(messages.labels.title)).to.exist);

            /* ASSERT */
            assertInjectionUserDetails(user, container);
        });
    });

    describe("User roles", () => {
        test("Designer", async () => {
            /* ARRANGE */
            const user = {
                id: 10,
                address: "Avenida Reina Mercedes, 16, 4B",
                city: "Sevilla",
                email: "davidhernandez@gmail.com",
                first_name: "David",
                is_designer: true,
                is_printer: false,
                last_name: "Hernández de la Prada",
                postal_code: 41012
            };

            mockFetch(user);

            /* ACT */
            const { container } = loadRender();

            await waitFor(() => expect(screen.getByText(messages.labels.title)).to.exist);

            /* ASSERT */
            expect(() => expect(screen.getByText("Diseñador")).to.exist);
        });

        test("Printer", async () => {
            /* ARRANGE */
            const user = {
                id: 10,
                address: "Avenida Reina Mercedes, 16, 4B",
                city: "Sevilla",
                email: "davidhernandez@gmail.com",
                first_name: "David",
                is_designer: false,
                is_printer: true,
                last_name: "Hernández de la Prada",
                postal_code: 41012
            };

            mockFetch(user);

            /* ACT */
            const { container } = loadRender()

            await waitFor(() => expect(screen.getByText(messages.labels.title)).to.exist);

            /* ASSERT */
            expect(() => expect(screen.getByText("Impresor")).to.exist);
        });
    });
});

// Auxiliar functions
function assertOKUserDetails(user, container) {
    const checkText = ["address", "city", "email", "first_name", "last_name"];

    for (let i = 0; i < checkText.length; i++) {
        const expectedText = new RegExp(user[checkText[i]]);
        expect(() => screen.queryByText(expectedText)).to.exist;
    }
}

function assertInjectionUserDetails(user, container) {
    const checkText = ["address", "city", "email", "first_name", "last_name"];

    for (let i = 0; i < checkText.length; i++) {
        const expectedText = parseScriptAndHtml(user[checkText[i]]);
        expect(() => screen.queryByText(expectedText)).to.exist;
    }
}

function mockFetch(object) {
    vi.spyOn(window, 'fetch').mockImplementationOnce(() => {
        return Promise.resolve({
            ok: true,
            json: () => Promise.resolve(object),
        });
    });
}

function parseScriptAndHtml(input) {
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

