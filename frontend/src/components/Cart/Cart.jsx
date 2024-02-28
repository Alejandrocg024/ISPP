import React, { useEffect, useState } from 'react';
import './Cart.css';
import { FaTrash } from "react-icons/fa";
import Text, { TEXT_TYPES } from '../Text/Text';

const backend = JSON.stringify(import.meta.env.VITE_APP_BACKEND);
const frontend = JSON.stringify(import.meta.env.VITE_APP_FRONTEND);

const Cart = ({
  cart,
  setCart,
}) => {
  const [buyerEmail, setBuyerEmail] = useState('');
  const [address, setAddress] = useState('');
  const [city, setCity] = useState('');
  const [postalCode, setPostalCode] = useState(0);
  const [errors, setErrors] = useState({});

  useEffect(() => {
    const fetchData = async () => {
      try {
        let petition = backend + '/designs/loguedUser';
        petition = petition.replace(/"/g, '');
        const response = await fetch(petition, {
          headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
        });
        const datos = await response.json();
        // Actualizar el estado con los datos obtenidos
        setBuyerEmail(datos.email);
        setPostalCode(datos.postal_code);
        setCity(datos.city);
        setAddress(datos.address);
      } catch (error) {
        console.log(error);
      }
    };
  
    fetchData();
   
  }, []);

  const deleteProduct = product => {
    const results = cart.filter(
      item => item.id !== product.id
    );

    setCart(results);
  };

  const editProduct = (product, amount) => {
    let cartCopy = [...cart];
    let existingProduct = cartCopy.find(cartProduct => cartProduct.id === product.id);
    if (!existingProduct || (product.stock_quantity - existingProduct.quantity) < amount) return;
    existingProduct.quantity += amount;
    if (existingProduct.quantity <= 0) {
      cartCopy = cart.filter(item => item.id !== product.id);
    }
    setCart(cartCopy);
    localStorage.setItem('cart', JSON.stringify(cart));
  };

  const handleCheckout = async (e) => {
    e.preventDefault(); 

    setErrors({});

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(buyerEmail)) {
      errors.buyerEmail = 'El correo electrónico no es válido';
      setErrors(errors);
    }    

    if (buyerEmail.length>255){
      errors.buyerEmail = 'El correo electrónico no puede tener más de 255 caracteres';
      setErrors(errors);
    }

    if (address.length>255){
      errors.address = 'La dirección no puede tener más de 255 caracteres';
      setErrors(errors);
    }

    if (city.length>50){
      errors.city = 'La ciudad no puede tener más de 50 caracteres';
      setErrors(errors);
    }

    if (postalCode<1000 || postalCode>52999){
      errors.postalCode = 'El código postal debe estar entre 1000 y 52999';
      setErrors(errors);
    }

    if (Object.keys(errors).length > 0) return;

    try {
      const formData = new FormData();
      formData.append('cart', JSON.stringify(cart));
      formData.append('buyer_mail', buyerEmail);
      formData.append('address', address);
      formData.append('city', city);
      formData.append('postal_code', postalCode);
      let petition = backend + '/newOrder';
      petition = petition.replace(/"/g, '');
      
      // Hacer la petición y esperar la respuesta
      const response = await fetch(petition, {
        method: 'POST',
        body: formData
      });
  
      // Verificar si la respuesta es satisfactoria
      if (response.ok) {
        // Obtener el cuerpo de la respuesta como JSON
        const responseData = await response.json();
        // Obtener la URL de pago de PayPal desde los datos de respuesta
        const paypalPaymentUrl = responseData.paypal_payment_url; 
        // Redirigir a la URL de pago de PayPal
        setCart([]);
        window.location.href = paypalPaymentUrl;
      } else {
        // Si la respuesta no es satisfactoria, mostrar un mensaje de error
        alert('Error al realizar la compra');
      }
    } catch(error) {
      // Si hay un error, mostrar un mensaje de error
      alert('Error al realizar la compra');
    }
  };
    

  const totalPrice = () => {
    return cart.reduce((total, product) => total + (parseFloat(product.price) * parseFloat(product.quantity)), 0);
  };

  return (
    <div className='wrapper'>
      <h1>Mi carrito</h1>
      <div className="project">
        <div className="shop">
          {cart.map(product => (
            <div className='box' key={product.id}>
              <div className='img-container'> 
                <img src={'/images/' + product.imageRoute} alt={product.name} />
              </div>
              <div className="content">
                <div>
                  <h3>Nombre: {product.name}</h3>
                  <h3>Precio: {product.price}€</h3>
                </div>
                <div className='cart-right'>
                  <a className='trash' onClick={() => deleteProduct(product)}>
                    <FaTrash />
                  </a>
                  <div className='button-container'>
                    <button className="cart-qty-plus" type="button" onClick={() => editProduct(product, -1)} value="-">-</button>
                    <input type="text" name="qty" min="0" className="qty form-control" value={product.quantity} readOnly />
                    <button className="cart-qty-minus" type="button" onClick={() => editProduct(product, 1)} value="+">+</button>
                  </div>
                </div>
              </div>
            </div>
          ))}
          <div className="right-bar">
            <p><span>Subtotal</span> <span>{totalPrice()} €</span></p>
            <hr />
            <p><span>Envío</span> <span>5 €</span></p>
            <p><span>Total envío</span> <span></span></p>
            <hr />
            <p><span>Total</span> <span>{totalPrice() + 5} €</span></p>
            <div className='checkout-form'>
              <h2>Datos del comprador</h2>
              <div class='form'>
                <form>
                  <div className='form-group'>
                    <label className='buyer_mail'>Correo electrónico:</label>
                    <input type='text' id='buyer_mail' name='buyer_mail' value={buyerEmail} className='form-input' onChange={e => setBuyerEmail(e.target.value)} required />
                    {errors.buyerEmail && <p className='error-message'>{errors.buyerEmail}</p>}
                  </div>
                  <div className="form-group">
                    <label className='address'>Dirección:</label>
                    <input type='text' id='address' name='address' value={address} className='form-input' onChange={e => setAddress(e.target.value)} required />
                    {errors.address && <p className='error-message'>{errors.address}</p>}
                  </div>
                  <div className="form-group">
                    <label className='city'>Ciudad:</label>
                    <input type='text' id='city' name='city'  value={city} className='form-input' onChange={e => setCity(e.target.value)} required />
                    {errors.city && <p className='error-message'>{errors.city}</p>}
                  </div>
                  <div className="form-group">
                    <label className='postal_code'>Código Postal:</label>
                    <input type='number' id='postal_code' name='postal_code' min={1000} max={52999} value={postalCode} className='form-input' onChange={e => setPostalCode(e.target.value)} required />
                    {errors.postalCode && <p className='error-message'>{errors.postalCode}</p>}
                  </div>
                  <button onClick={handleCheckout}>Finalizar la compra</button>
                </form>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Cart;