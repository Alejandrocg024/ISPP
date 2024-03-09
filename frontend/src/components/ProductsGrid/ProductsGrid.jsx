import React, { useEffect, useState } from 'react'
import './ProductsGrid.css'
import Product from '../Product/Product';
import Text, { TEXT_TYPES } from '../Text/Text';

const backend = JSON.stringify(import.meta.env.VITE_APP_BACKEND);
const frontend = JSON.stringify(import.meta.env.VITE_APP_FRONTEND);

const ProductsGrid = (consts) => {

    const { gridType, elementType } = consts

    const getGridClass = () => {
        return gridType.toLowerCase() + '-gr grid';
    }

    const getAllProducts = async (elementType) => {
        try {
            let petition = backend + '/products/api/v1/products/?product_type=' + elementType;
            petition = petition.replace(/"/g, '')
            const response = await fetch(petition, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                const data = await response.json();
                return data;
            } else {
                console.error('Error al obtener los productos');
            }
        } catch (error) {
            console.error('Error al comunicarse con el backend:', error);
        }
    }

    const groupProducts = async (elementType) => {
        try {
            const products = await getAllProducts(elementType);

            const groupsOfProducts = products.reduce((acc, product, index) => {
                const groupIndex = Math.floor(index / 5);
                if (!acc[groupIndex]) {
                    acc[groupIndex] = [];
                }
                acc[groupIndex].push(product);
                return acc;
            }, []);

            return groupsOfProducts;
        } catch (error) {
            console.error('Error al obtener y agrupar los productos: ', error);
        }
    }

    const [products, setProducts] = useState([]);

    useEffect(() => {

        async function loadProducts() {
            const res = await getAllProducts(elementType);

            if (res && Array.isArray(res)) { // Verificar si res no es undefined y es un array
                {/*Adaptar código cuando se añada funcionalidad de destacados*/}
                if (gridType === GRID_TYPES.MAIN_PAGE) {
                    setProducts(res.slice(0, 5));
                } else {
                    const groupsOfProducts = await groupProducts(elementType);
                    setProducts(groupsOfProducts);
                }
            }
        }
        loadProducts();

    }, [gridType, elementType]);

    return (
        <div className={getGridClass()}>
            {gridType === GRID_TYPES.UNLIMITED ? (
                <>
                    <Text type={TEXT_TYPES.TITLE_BOLD} text='Diseños' />
                    <div className='products-container'>
                        {products.map((group, groupIndex) => (
                            <div key={groupIndex} className={`products-row ${group.length < 5 ? 'last' : ''}`}>
                                {group.map((product) => (
                                    <Product name={product.name} price={product.price} pathImage={product.image_url ? product.image_url : product.imageRoute} pathDetails={product.id} isImageRoute={!product.image_url} />
                                ))}
                            </div>
                        ))}
                    </div>
                </>
            ) : (
                products.map(product => (
                    <div key={product.id}>
                        <Product name={product.name} price={product.price} pathImage={product.image_url ? product.image_url : product.imageRoute} pathDetails={product.id} isImageRoute={!product.image_url} />
                    </div>
                ))
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
