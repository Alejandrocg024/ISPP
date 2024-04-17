import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import './AddProduct.css';
import PageTitle from './PageTitle/PageTitle';
import Text, { TEXT_TYPES } from "./Text/Text";

const backend = JSON.stringify(import.meta.env.VITE_APP_BACKEND);
const frontend = JSON.stringify(import.meta.env.VITE_APP_FRONTEND);

const EditProduct = () => {
  const { id } = useParams();
  const [state, setState] = useState({
    productId: id,
    file: null,
    design: null,
    name: '',
    description: '',
    show: false,
    price: 0,
    stockQuantity: 1,
    imagePreview: '',
    errors: {},
    productType: '',
    currentUserId: null,
    seller_plan: false,
    designer_plan: false,
    countShow: 0,
  });

  useEffect(() => {
    const fetchProductData = async () => {
      let petition = backend + '/products/api/v1/products/' + id + '/get_product_data/';
      petition = petition.replace(/"/g, '')
      try {
        const response = await fetch(petition);
        if (!response.ok) {
          throw new Error('Error al cargar los detalles del producto');
        }
        const productData = await response.json();
        setState(prevState => ({
          ...prevState,
          name: productData.name,
          description: productData.description,
          show: productData.show,
          price: productData.price,
          stockQuantity: productData.stock_quantity,
          imagePreview: productData.image_url,
          productType: productData.product_type,
          design: productData.design,
        }));
        console.log('Detalles del producto cargados correctamente:', productData);

        let petition2 = backend + '/designs/loguedUser';
        petition2 = petition2.replace(/"/g, '');
        const response_currentUser = await fetch(petition2, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });
        if (response_currentUser.ok) {
          const currentUserData = await response_currentUser.json();

          if (currentUserData.id !== productData.seller) {
            alert("No tienes permiso para editar este producto.");
            window.location.href = '/';
          }

          setState(prevState => ({
            ...prevState,
            currentUserId: currentUserData.id,
            seller_plan: currentUserData.seller_plan,
            designer_plan: currentUserData.designer_plan,
          }));

          let petitionProducts = backend + '/products/api/v1/products/?seller=' + currentUserData.id;
          petitionProducts = petitionProducts.replace(/"/g, '');
          const responseProducts = await fetch(petitionProducts, {
            method: 'GET',
            headers: {
              'Content-Type': 'application/json'
            }
          });
          if (responseProducts.ok) {
            const products = await responseProducts.json();
            let count = 0;
            products.forEach(product => {
              
              if (product.show && product.id.toString() !== id) {
                count++;
              }
            });
            setState(prevState => ({
              ...prevState,
              countShow: count,
            }));
          } else {
            console.error('Error al obtener los productos');
          }
        }
      } catch (error) {
        console.error('Error al cargar los detalles del producto:', error);
        alert('Error al cargar los detalles del producto');
      }
    };

    fetchProductData();
  }, [id]);


  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0];
    const allowedExtensions = ["jpg", "jpeg", "png"];
    const fileExtension = selectedFile ? selectedFile.name.split('.').pop().toLowerCase() : null;

    if (!selectedFile) {
      setState(prevState => ({ ...prevState, file: null }));
      return;
    }

    if (!allowedExtensions.includes(fileExtension)) {
      setState(prevState => ({ ...prevState, file: null, errors: { file: 'Por favor, seleccione un archivo de imagen válido (.jpg, .jpeg, .png)' } }));
      return;
    }

    setState(prevState => ({ ...prevState, file: selectedFile }));

    if (selectedFile) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setState(prevState => ({ ...prevState, imagePreview: reader.result }));
      };
      reader.readAsDataURL(selectedFile);
    }
  };

  const handleDesignChange = (event) => {
    const design = event.target.files[0];
    if (!design) {
      return;
    }
    const fileName = design.name;
    const fileExtension = fileName.split('.').pop().toLowerCase();
    if (fileExtension !== 'stl') {
      alert('El archivo no es de formato STL. Por lo tanto lo ignoraremos. Por favor, sube un archivo STL.');
      event.target.value = ''; 
      return;
    }else{
      setState(prevState => ({ ...prevState,  design: design }));
    }
  }

  const validateForm = () => {
    const { name, description, price, stockQuantity, productType, seller_plan, designer_plan, countShow, show, design } = state;
    const errors = {};

    if (productType === 'D' && !design) {
      errors.file = 'Por favor, seleccione un archivo de diseño';
    }

    if (!name.trim()) {
      errors.name = 'El nombre es obligatorio';
    }

    if(name.trim().length<3||name.length>30){
      errors.name = 'El nombre debe tener entre 3 y 30 caracteres';
    }

    if (!description.trim()) {
      errors.description = 'La descripción es obligatoria';
    }

    if(description.trim().length<20||description.length>200){
      errors.description = 'La descripción debe tener entre 20 y 200 caracteres';
    }

    if(show && seller_plan && designer_plan && countShow >= 8){
      errors.show = 'No puedes más destacar más de 8 productos';
    } else if(show && !seller_plan && designer_plan && countShow >= 3){
      errors.show = 'Para destacar más de 3 productos necesitas un plan de vendedor';
    } else if(show && seller_plan && !designer_plan && countShow >= 5){
      errors.show = 'Para destacar más de 5 productos necesitas un plan de diseñador';
    } else if (show && !seller_plan && !designer_plan) {
      errors.show = 'Para destacar productos debe adquirir un plan';
    }

    if (!/^\d+(\.\d{1,2})?$/.test(price)) {
      errors.price = 'El precio debe tener el formato correcto (por ejemplo, 5.99)';
    } else if (parseFloat(price) <= 0 || parseFloat(price) >= 1000000) {
      errors.price = 'El precio debe estar entre 0 y 1,000,000';
    }

    if (productType === 'D') {
      if (stockQuantity !== 1) {
        errors.stockQuantity = 'Para productos de tipo diseño, la cantidad debe ser 1';
      }
    } else {
      const stockQuantityValue = parseInt(stockQuantity);
      if (isNaN(stockQuantityValue) || stockQuantityValue < 1 || stockQuantityValue > 100 || Number(stockQuantity) !== stockQuantityValue) {
        errors.stockQuantity = 'La cantidad debe ser un número entero entre 1 y 100';
      }
    }

    setState(prevState => ({ ...prevState, errors }));

    return Object.keys(errors).length === 0;
  };


  const handleSubmit = (event) => {
    event.preventDefault();

    if (validateForm()) {
      const formData = new FormData();
      if (state.file) {
        formData.append('file', state.file);
      }
      if (state.design) {
        formData.append('design', state.design);
      }
      formData.append('name', state.name);
      formData.append('description', state.description);
      formData.append('show', state.show);
      formData.append('price', state.price);
      formData.append('stock_quantity', state.stockQuantity);
      let petition = backend + '/products/api/v1/products/' + state.productId + '/edit_product/';
      petition = petition.replace(/"/g, '');
      fetch(petition, {
        method: 'PUT',
        headers: {
          'Authorization': 'Bearer ' + localStorage.getItem('token')
        },
        body: formData
      })
        .then(response => {
          if (response.ok) {
            alert('Producto actualizado correctamente');
            const productId = id.replace(/"/g, '');
            const editUrl = `/product-details/${productId}/`;
            window.location.href = editUrl;
          } else {
            throw new Error('Error al actualizar el producto');
          }
        })
        .catch(error => {
          console.error('Error al enviar el formulario:', error);
          alert('Error al enviar el formulario');
        });
    } else {
      return;
    }
  };

  return (
    <>
      <div className="upload-product-page">

        <PageTitle title="Subir producto" />
        <div className="upload-product-title-container">
          <Text type={TEXT_TYPES.TITLE_BOLD} text='Editar producto' />
        </div>

        <div className="upload-product-container">

          <div className="left-upload-product-container">
            <div className="product-image">
              {state.imagePreview && <img src={state.imagePreview} alt='Preview' className='product-image-preview'/>}
            </div>
          </div>
          <div className="right-upload-product-container">
            <div className="upload-product-data-container">
              <h2 className="upload-product-data-section-title">Datos sobre el producto</h2>

              <form className="upload-product-data-form" onSubmit={handleSubmit}>
                <div className='form-group'>
                  {state.file && <p className="image-name"><strong>Imagen seleccionada: </strong>{state.file.name}</p>}
                  <label htmlFor="file" className={state.file ? "upload-image-button loaded" : "upload-image-button"}>{state.file ? "Cambiar imagen" : "Seleccionar imagen"}</label>
                  <input type='file' id='file' name='file' className='form-input upload' accept='.jpg, .jpeg, .png' onChange={handleFileChange} />
                  {state.errors.file && <div className="error">{state.errors.file}</div>}
                </div>

                {state.productType === 'D' && (
                  <div className='form-group'>
                    {state.design && <p className="design-name"><strong>Diseño seleccionado: </strong>{state.design.name}</p>}
                    <label htmlFor="file2" className={state.design ? "upload-design-button loaded" : "upload-design-button"}>{state.design ? "Cambiar diseño" : "Seleccionar diseño"}</label>
                    <input type='file' id='file2' name='file2' className='form-input upload' accept='.stl' onChange={handleDesignChange} />
                    {state.errors.design && <div className="error">{state.errors.design}</div>}
                  </div>
                )}

                <div className='form-group'>
                  <label htmlFor='name' className='name label'>Nombre</label>
                  <input type='text' id='name' name='name' className='form-input' value={state.name} onChange={(e) => setState(prevState => ({ ...prevState, name: e.target.value }))} placeholder="Cerdito rosa" />
                  {state.errors.name && <div className="error">{state.errors.name}</div>}
                </div>

                <div className='form-group'>
                  <label htmlFor='description' className='description label'>Descripción</label>
                  <textarea id='description' name='description' className='form-input' value={state.description} onChange={(e) => setState(prevState => ({ ...prevState, description: e.target.value }))} placeholder="Pieza de un cerdo con dimensiones de 20x12 cm, perfecto estado" />
                  {state.errors.description && <div className="error">{state.errors.description}</div>}
                </div>

                {state.productType !== 'D' && (
                  <div className='form-group'>
                    <label htmlFor='stock-quantity' className='stock_quantity label'>Cantidad</label>
                    <input type='number' id='stock-quantity' name='stock-quantity' className='form-input' value={state.stockQuantity} min={1} max={100} onChange={(e) => setState({ stockQuantity: e.target.value })} placeholder="2" />
                    {state.errors.stockQuantity && <div className="error">{state.errors.stockQuantity}</div>}
                  </div>
                )}

                <div className='form-group'>
                  <label htmlFor='price' className='price label'>Precio</label>
                  <input type='text' id='price' name='price' className='form-input' value={state.price} onChange={(e) => setState(prevState => ({ ...prevState, price: e.target.value }))} placeholder="5.99" />
                  {state.errors.price && <div className="error">{state.errors.price}</div>}
                </div>

                <div className='form-group'>
                  <div className="form-group-contents">
                    <input type='checkbox' id='show' name='show' checked={state.show} onChange={(e) => setState(prevState => ({ ...prevState, show: e.target.checked }))} />
                    <label htmlFor='show' className='show label'>Destacar el producto</label>
                  </div>
                  {state.errors.show && <div className="error">{state.errors.show}</div>}
                </div>
              </form>
            </div>
            <button className='large-btn button' type='button' onClick={handleSubmit}>Editar producto</button>
          </div>

        </div>

      </div> 
    </>
  );
};

export default EditProduct;
