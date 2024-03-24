import React, { useEffect, useState } from 'react'
import './ProductsGrid.css'
import Product from '../Product/Product';
import Text, { TEXT_TYPES } from '../Text/Text';
import Paginator from '../Paginator/Paginator';

const backend = JSON.stringify(import.meta.env.VITE_APP_BACKEND);
const frontend = JSON.stringify(import.meta.env.VITE_APP_FRONTEND);

const ProductsGrid = (consts) => {

    const { gridType, elementType, filter, main } = consts

    const getGridClass = () => {
        return gridType.toLowerCase() + '-gr grid';
    }

    const getAllProducts = async (elementType, filter) => {
        try {
            let petition = backend + '/products/api/v1/products/';
            if (filter) {
                petition += filter;
            } else if (elementType) {
                petition += '?product_type=' + elementType;
            }
            petition = petition.replace(/"/g, '')
            const response = await fetch(petition, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                const data = await response.json();
                if(main){
                    return data.filter(product => product.show === true);
                }
                return data;
            } else {
                console.error('Error al obtener los productos');
            }
        } catch (error) {
            console.error('Error al comunicarse con el backend:', error);
        }
    }

    const groupProducts = (products) => {
        try {

            const groupsOfProducts = products.reduce((acc, product, index) => {
                let groupIndex = Math.floor(index / 5);
                console.log('groupIndex', groupIndex)
                if (window.innerWidth > 767 && window.innerWidth < 1024) {
                    groupIndex = Math.floor(index / 3);
                } else if (window.innerWidth < 768) {
                    groupIndex = Math.floor(index / 2);
                }
                if (!acc[groupIndex]) {
                    acc[groupIndex] = [];
                }
                acc[groupIndex].push(product);
                return acc;
            }, []);

            return groupsOfProducts;

        } catch (error) {
            console.error('Error al obtener y agrupar los productos: ', error);
            return [];
        }
    }

    const transformTypeName = (elementType) => {
        switch (elementType) {
            case 'D':
                return 'Diseños';
            case 'I':
                return 'Piezas';
            case 'P':
                return 'Impresoras';
            case 'M':
                return 'Materiales';
            default:
                return 'Productos';
        }
    }

    const [products, setProducts] = useState([]);
    const [page, setPage] = useState(1);
    const [productsPerPage, setProductsPerPage] = useState(25);
    const [numPages, setNumPages] = useState(0);

    useEffect(() => {

        async function loadProducts() {
            const res = await getAllProducts(elementType, filter);

            if (res && Array.isArray(res)) { // Verificar si res no es undefined y es un array
                {/*Adaptar código cuando se añada funcionalidad de destacados*/}
                if (gridType === GRID_TYPES.MAIN_PAGE) {
                    setProducts(res.sort(() => Math.random() - 0.5).slice(0, 5));
                } else {
                    if (window.innerWidth < 768) {
                        setProductsPerPage(12);
                    } else if (window.innerWidth > 767 && window.innerWidth < 1024) {
                        setProductsPerPage(15);
                    }
                    const numPages = Math.ceil(res.length / productsPerPage);
                    setNumPages(numPages);
                    const allProducts = res.slice((page - 1) * productsPerPage, page * productsPerPage);
                    const groupsOfProducts = groupProducts(allProducts);
                    setProducts(groupsOfProducts);
                }
            }
        }
        loadProducts();

    }, [gridType, elementType, filter, page, productsPerPage, main]);

    return (
        <div className={getGridClass()}>
            {gridType === GRID_TYPES.UNLIMITED ? (
                <div className='products-container'>
                    <Text type={TEXT_TYPES.TITLE_BOLD} text={transformTypeName(elementType)} />
                    {products.map((group, groupIndex) => (
                        <div key={`group-${groupIndex}`} className={`products-row ${group.length < 5 ? 'last' : ''}`}>
                            {group.map((product, productIndex) => (
                                <Product name={product.name} price={product.price} pathImage={product.image_url ? product.image_url : product.imageRoute} pathDetails={product.id} isImageRoute={!product.image_url} key={`product-${groupIndex}-${productIndex}`} />
                            ))}
                        </div>
                    ))}
                    <Paginator page={page} setPage={setPage} numPages={numPages} />
                </div>
            ) : (
                <>
                    {products.length === 0 ? (
                        <p className='empty-grid-text'>Actualmente, no hay productos para mostrar.</p>
                    ) : (
                        products.map(product => (
                            <div key={product.id}>
                                <Product name={product.name} price={product.price} pathImage={product.image_url ? product.image_url : product.imageRoute} pathDetails={product.id} isImageRoute={!product.image_url} />
                            </div>
                        ))
                    )}
                </>
            )}
        </div>
    )
}

export default ProductsGrid

export const GRID_TYPES = {
    MAIN_PAGE: 'MAIN-PAGE',
    UNLIMITED: 'UNLIMITED',
    PAGINATED: 'PAGINATED',
}

export const ELEMENT_TYPES = {
    DESIGN: 'D',
    IMPRESSION: 'I',
    PRINTER: 'P',
    MATERIAL: 'M',
}
