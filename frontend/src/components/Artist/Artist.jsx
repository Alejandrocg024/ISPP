import React from 'react'
import './Artist.css'
import filledStar from '../../assets/bxs-star.svg'
import emptyStar from '../../assets/bx-star.svg'
import defaultImage from '../../assets/default_artist_image.png'

const frontend = JSON.stringify(import.meta.env.VITE_APP_FRONTEND);

const Artist = (props) => {

    const { username, pathImage, pathDetails } = props

    const onButtonClick = () => {
        if (!pathDetails) {
            window.location.href = '/';
        } else {
            window.location.href = JSON.parse(frontend) + `/user-details/${pathDetails}`;
        }
    }

    function modifyImagePath(pathImage) {
        let imagePath = defaultImage;

        if (pathImage) {
            imagePath = 'images/' + pathImage;
        }

        return imagePath;
    }
    const imageRoute = modifyImagePath(pathImage);

    return (
        <div className='artist' onClick={onButtonClick}>
            
            <div className='artist-image'>
                <img src={pathImage || defaultImage} className='image'/>
            </div>

            <div className='artist-description'>
                <p className='name'>{username}</p>
                {/* Sustituir por la lógica de opiniones en un futuro */}
                <div className='stars-container'>
                    <img src={filledStar} className='star' />
                    <img src={filledStar} className='star' />
                    <img src={filledStar} className='star' />
                    <img src={emptyStar} className='star' />
                    <img src={emptyStar} className='star' />
                </div>
            </div>

        </div>
    )
}

export default Artist