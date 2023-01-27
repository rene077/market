import Layout from '../hocs/Layout'
import { Fragment, useState, useEffect } from 'react'
import { Dialog, Disclosure, Menu, Transition } from '@headlessui/react'
import { XIcon } from '@heroicons/react/outline'
import { ChevronDownIcon, FilterIcon, MinusSmIcon, PlusSmIcon, ViewGridIcon } from '@heroicons/react/solid'
import { Link } from 'react-router-dom'
import { connect } from 'react-redux'
import {get_categories} from '../redux/actions/categories'
import {get_products, get_filtered_products} from '../redux/actions/products'
import ProductCard from '../components/product/ProductCard'
import { prices } from '../helpers/fixedPrices'

const sortOptions = [
  { name: 'Most Popular', href: '#', current: true },
  { name: 'Best Rating', href: '#', current: false },
  { name: 'Newest', href: '#', current: false },
  { name: 'Price: Low to High', href: '#', current: false },
  { name: 'Price: High to Low', href: '#', current: false },
]
const subCategories = [
  { name: 'Totes', href: '#' },
  { name: 'Backpacks', href: '#' },
  { name: 'Travel Bags', href: '#' },
  { name: 'Hip Bags', href: '#' },
  { name: 'Laptop Sleeves', href: '#' },
]
const filters = [
  {
    id: 'color',
    name: 'Color',
    options: [
      { value: 'white', label: 'White', checked: false },
      { value: 'beige', label: 'Beige', checked: false },
      { value: 'blue', label: 'Blue', checked: true },
      { value: 'brown', label: 'Brown', checked: false },
      { value: 'green', label: 'Green', checked: false },
      { value: 'purple', label: 'Purple', checked: false },
    ],
  },
  {
    id: 'category',
    name: 'Category',
    options: [
      { value: 'new-arrivals', label: 'New Arrivals', checked: false },
      { value: 'sale', label: 'Sale', checked: false },
      { value: 'travel', label: 'Travel', checked: true },
      { value: 'organization', label: 'Organization', checked: false },
      { value: 'accessories', label: 'Accessories', checked: false },
    ],
  },
  {
    id: 'size',
    name: 'Size',
    options: [
      { value: '2l', label: '2L', checked: false },
      { value: '6l', label: '6L', checked: false },
      { value: '12l', label: '12L', checked: false },
      { value: '18l', label: '18L', checked: false },
      { value: '20l', label: '20L', checked: false },
      { value: '40l', label: '40L', checked: true },
    ],
  },
]

function classNames(...classes) {
  return classes.filter(Boolean).join(' ')
}

const Shop = ({
    get_categories,
    categories,
    get_products,
    products,
    get_filtered_products,
    filtered_products
}) => {
    const [mobileFiltersOpen, setMobileFiltersOpen] = useState(false)
    const [filtered, setFiltered] = useState(false)   //VAR QUE SERVIRÁ DE VERIFICACION 

        //CREACION DEL FORMULARIO-FILTRO  
    const [formData, setFormData] = useState({
      category_id: '0',
      price_range: 'Any',
      sortBy: 'created',
      order: 'desc'
    })

    const { 
      category_id,
      price_range,
      sortBy,
      order
    } = formData

    //FUNCIONES QUE DEBEN ARRANCAR INICIALMENTE PARA DISPONER DE LOS DATOS
    useEffect(() => {
        get_categories()
        get_products()
        window.scrollTo(0,0)
    }, [])

    //ACTUALIZACION DE DATOS INSTANTANEOS DE HABER MODIFS EN LOS INPUTS
    const onChange = e => setFormData({ ...formData, [e.target.name]: e.target.value})

    //EL BOTTON DE ENVIO DE DATOS A PROCESO -> [RESPUESTA]
    const onSubmit = e => {
      e.preventDefault()
      get_filtered_products( category_id, price_range, sortBy , order)  //YA TIENE ALGO PREDETERMINADO EL ENVIO DE DATOS, 
      setFiltered(true)                                                 //ESPERAMOS CAMBIOS PARA FILTRAR ACORDE A LO SOLICITADO     
    }

    //PARA MOSTRAR LOS RESULTADOS FINALES 
    const showProducts = () => {                       
      let results = []
      let display = []

      if (                                              //SI TODO ESTO ESTA OK, ENTONCES 
        filtered_products &&
        filtered_products !== null &&
        filtered_products !== undefined &&
        filtered
      ) {
        filtered_products.map((product, index) => {         //RECORREMOS Y PASAMOS PRODUCTS AL ARRAY DISPLAY 
            return display.push(
                <div key={index}>
                    <ProductCard product={product}/>            {/* CAJA CHICA IRA A CAJA GRANDE */}
                </div>
            );
        });
      } else if (                                       //DE LO CONTRARIO ,SÍ ESTO ES ASÍ ,MUESTRA LO MISMO PRODUCTS SIN FILTRO  
          !filtered && 
          products &&
          products !== null && 
          products !== undefined
      ) {
          products.map((product, index) => {                     
            return display.push(
                <div key={index}>
                    <ProductCard product={product}/>            {/* CAJA CHICA IRA A CAJA GRANDE */}
                </div>
            );
        });
      }

      for (let i = 0; i < display.length; i += 3) {          //CAJA GRANDE RECIBE Y MUESTRA A CAJA CHICA(display) EN COLUMNAS
        results.push(                    //salta a i=3 para que muestre la otra tanda,pues ya mostro los primeros 3 elementos
          <div key={i} className='grid md:grid-cols-3 '>
              {display[i] ? display[i] : <div className=''></div>}
              {display[i+1] ? display[i+1] : <div className=''></div>}
              {display[i+2] ? display[i+2] : <div className=''></div>}
          </div>
        )
      }

      return results

    }



    return (
        <Layout>
        <div className="bg-white">
          <div>

                      {/* FILTRO MOBILE "B" RESPONSIVE */}
          <Transition.Root show={mobileFiltersOpen} as={Fragment}>

                        {/* FILTRO MOBILE "B" */}
            <Dialog as="div" className="fixed inset-0 flex z-40 lg:hidden" onClose={setMobileFiltersOpen}>
              <Transition.Child
                as={Fragment}
                enter="transition-opacity ease-linear duration-300"
                enterFrom="opacity-0"
                enterTo="opacity-100"
                leave="transition-opacity ease-linear duration-300"
                leaveFrom="opacity-100"
                leaveTo="opacity-0"
              >
                <Dialog.Overlay className="fixed inset-0 bg-black bg-opacity-25" />
              </Transition.Child>

              <Transition.Child
                as={Fragment}
                enter="transition ease-in-out duration-300 transform"
                enterFrom="translate-x-full"
                enterTo="translate-x-0"
                leave="transition ease-in-out duration-300 transform"
                leaveFrom="translate-x-0"
                leaveTo="translate-x-full"
              >

                <div className="ml-auto relative max-w-xs w-full h-full bg-white shadow-xl py-4 pb-12 flex flex-col overflow-y-auto">
                  <div className="px-4 flex items-center justify-between">
                    <h2 className="text-lg font-medium text-gray-900">Filters</h2>
                    <button
                      type="button"
                      className="-mr-2 w-10 h-10 bg-white p-2 rounded-md flex items-center justify-center text-gray-400"
                      onClick={() => setMobileFiltersOpen(false)}
                    >
                      <span className="sr-only">Close menu</span>
                      <XIcon className="h-6 w-6" aria-hidden="true" />
                    </button>
                  </div>

                      {/* FILTRO MOBILE "B" (IS RESPONSIVE) */}
                  <form onSubmit={e => onSubmit(e)} className="mt-4 border-t border-gray-200">
                    <h3 className="sr-only">Categories</h3>

                            {/* LISTADO DE CATEGORIAS CON SUS SUBCATEGORIAS */}
                    <ul role="list" className="font-medium text-gray-900 px-2 py-3">
                      {
                          categories &&
                          categories !== null &&
                          categories !== undefined &&
                          categories.map(category => {          //SÍ EXISTE CATEGORIES "RECORREMOS TODAS" COMO CATEGORY INDIV 1 A 1
                              if (category.sub_categories.length === 0){         //ENTRA EL 1ro SÍ NO TIENE SUBCATEGORIES
                                  return (
                                      <div key={category.id} className=' flex items-center h-5 my-5'>
                                          <input
                                              name='category_id'
                                              onChange={e => onChange(e)}           //PARA RECEPTAR CUALQUIER CAMBIO
                                              value={category.id.toString()}        //LE ASIGNA EL NOMBRE QUE TRAE LA FUNCTION
                                              type='radio'
                                              className='focus:ring-blue-500 h-4 w-4 text-blue-600 border-gray-300 rounded-full'
                                          />
                                          <label className="ml-3 min-w-0 flex-1 text-gray-500">
                                              {category.name}
                                          </label>
                                      </div>
                                  )
                              } else {                  //AL TENER SUBCATEGS MUESTRO LO MISMO Y LE SUMO LAS SUBCATEGS CONSIGUIENTE
                                  let result = []
                                  result.push(
                                      <div key={category.id} className='flex items-center h-5'>
                                          <input
                                              name='category_id'
                                              onChange={e => onChange(e)}
                                              value={category.id.toString()}
                                              type='radio'
                                              className='focus:ring-blue-500 h-4 w-4 text-blue-600 border-gray-300 rounded-full'
                                          />
                                          <label className="ml-3 min-w-0 flex-1 text-gray-500">
                                              {category.name}
                                          </label>
                                      </div>
                                  )

                                  category.sub_categories.map(sub_category => {        //RECORRO LAS SUBCATEGS COMO SUB_CATEGORYS
                                      result.push(                                      //A LA VEZ QUE LE VAMOS AGREGANDO A CATEGORY
                                          <div key={sub_category.id} className='flex items-center h-5 ml-2 my-5'>
                                              <input
                                                  name='category_id'
                                                  onChange={e => onChange(e)}
                                                  value={sub_category.id.toString()}
                                                  type='radio'
                                                  className='focus:ring-blue-500 h-4 w-4 text-blue-600 border-gray-300 rounded-full'
                                              />
                                              <label className="ml-3 min-w-0 flex-1 text-gray-500">
                                                  {sub_category.name}
                                              </label>
                                          </div>
                                      )
                                  })

                                  return result                                      //MOSTRAMOS LA SEGUNDA OPTION CON SUS SUBCATEGS
                              }
                          })
                      }
                    </ul>

                              {/* FILTRO POR PRECIOS-PRICES */}
                    <Disclosure as="div" className="border-t border-gray-200 px-4 py-6">
                    {({ open }) => (
                      <>
                      <h3 className="-mx-2 -my-3 flow-root">

                            {/* BOTTON PARA MAXIMIZAR O MINIMIZAR MENUS */}
                        <Disclosure.Button className="px-2 py-3 bg-white w-full flex items-center justify-between text-gray-400 hover:text-gray-500">
                          <span className="font-sofiapro-regular text-gray-900">Prices</span>
                          <span className="ml-6 flex items-center">
                            {open ? (
                              <MinusSmIcon className="h-5 w-5" aria-hidden="true" />
                            ) : (
                              <PlusSmIcon className="h-5 w-5" aria-hidden="true" />
                            )}
                          </span>
                        </Disclosure.Button>

                              {/* DESPLIEGUE MENU DE PRECIOS-PRICES EJ: 1 - 19 */}
                        <Disclosure.Panel className="pt-6">
                          <div className="space-y-6">
                            {
                                prices && prices.map((price, index) => {
                                    if (price.id === 0) {
                                        return (
                                            <div key={index} className='form-check'>
                                                <input
                                                    onChange={e => onChange(e)}
                                                    value={price.name}
                                                    name='price_range'
                                                    type='radio'
                                                    className='focus:ring-blue-500 h-4 w-4 text-blue-600 border-gray-300 rounded-full'
                                                    defaultChecked
                                                />
                                                <label className='ml-3 min-w-0 flex-1 text-gray-500 font-sofiapro-light'>{price.name}</label>
                                            </div>
                                        )
                                    } else {
                                        return (
                                            <div key={index} className='form-check'>
                                                <input
                                                    onChange={e => onChange(e)}
                                                    value={price.name}
                                                    name='price_range'
                                                    type='radio'
                                                    className='focus:ring-blue-500 h-4 w-4 text-blue-600 border-gray-300 rounded-full'
                                                />
                                                <label className='ml-3 min-w-0 flex-1 text-gray-500 font-sofiapro-light'>{price.name}</label>
                                            </div>
                                        )
                                    }
                                })
                            }
                          </div>
                        </Disclosure.Panel>

                      </h3>
                      </>
                    )}
                    </Disclosure>

                            {/* MAS FILTROS _ POR SELECTION Y ORDER */}
                    <Disclosure as="div" className="border-t border-gray-200 px-4 py-6">
                    {({ open }) => (
                      <>
                      <h3 className="-mx-2 -my-3 flow-root">

                          {/* BOTTON PARA MAXIMIZAR O MINIMIZAR MENUS */}
                        <Disclosure.Button className="px-2 py-3 bg-white w-full flex items-center justify-between text-gray-400 hover:text-gray-500">
                          <span className="font-sofiapro-regular text-gray-900">Mas Filtros</span>
                          <span className="ml-6 flex items-center">
                            {open ? (
                              <MinusSmIcon className="h-5 w-5" aria-hidden="true" />
                            ) : (
                              <PlusSmIcon className="h-5 w-5" aria-hidden="true" />
                            )}
                          </span>
                        </Disclosure.Button>

                          {/* DESPLIEGUE DEL MENU SELECTION Y ORDER */}
                        <Disclosure.Panel className="pt-6">
                          <div className="space-y-6">
                            <div className='form-group '>
                                <label htmlFor='sortBy' className='mr-3 min-w-0 flex-1 text-gray-500'
                                >Ver por</label>
                                  <select
                                      className='my-2 font-sofiapro-light inline-flex justify-center w-full rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-gray-100 focus:ring-blue-500'
                                      id='sortBy'
                                      name='sortBy'
                                      onChange={e => onChange(e)}
                                      value={sortBy}
                                  >
                                    <option value='date_created'>Fecha</option>
                                    <option value='price'>Precio</option>
                                    <option value='sold'>Sold</option>
                                    <option value='title'>Nombre</option>

                                  </select>
                            </div>
                            <div className='form-group'>
                                <label htmlFor='order' className='mr-3 min-w-0 flex-1 text-gray-500'
                                >Orden</label>
                                <select
                                    className='my-2 font-sofiapro-light inline-flex justify-center w-full rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-gray-100 focus:ring-blue-500'
                                    id='order'
                                    name='order'
                                    onChange={e => onChange(e)}
                                    value={order}
                                >
                                    <option value='asc'>A - Z</option>
                                    <option value='desc'>Z - A</option>
                                </select>
                            </div>
                          </div>
                        </Disclosure.Panel>
                      </h3>
                      </>
                    )}
                    </Disclosure>

                            {/* BUTTON ENVIAR LOS FILTROS-CAMBIOS */}   
                    <button
                      type="submit"
                      className="float-right inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                    >
                      Buscar
                    </button>

                  </form>

                </div>
              </Transition.Child>
            </Dialog>
          </Transition.Root>


                      {/* FILTRO PRINCIPAL MAYOR "A" */}       
          <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">

                        {/* TITULO Y FILTRO "A" */}
            <div className="relative z-10 flex items-baseline justify-between pt-24 pb-6 border-b border-gray-200">
              <h1 className="text-4xl font-extrabold tracking-tight text-gray-900">Shop</h1>

              <div className="flex items-center">
                <button
                  type="button"
                  className="p-2 -m-2 ml-4 sm:ml-6 text-gray-400 hover:text-gray-500 lg:hidden"
                  onClick={() => setMobileFiltersOpen(true)}
                >
                  <span className="sr-only">Filters</span>
                  <FilterIcon className="w-5 h-5" aria-hidden="true" />
                </button>
              </div>
            </div>

                        {/* FILTRO "A" */}        
            <section aria-labelledby="products-heading" className="pt-6 pb-24">

              <h2 id="products-heading" className="sr-only">
                Products
              </h2>
                              {/* FILTRO "A" */}
              <div className="grid grid-cols-1 lg:grid-cols-4 gap-x-8 gap-y-10">

                {/* FILTRO OFICIAL MAYOR(NO RESPOSIVE)*/}
                <form onSubmit={e => onSubmit(e)} className="hidden lg:block">
                    <h3 className="sr-only">Categories</h3>

                        {/* LISTADO DE CATEGORIAS CON SUS SUBCATEGORIAS */}        
                    <ul role="list" className="font-medium text-gray-900 px-2 py-3">
                      {
                          categories &&
                          categories !== null &&
                          categories !== undefined &&
                          categories.map(category => {
                              if (category.sub_categories.length === 0){           //SÍ NO TIENE SUBCATEGORIAS
                                  return (
                                      <div key={category.id} className=' flex items-center h-5 my-5'>
                                          <input
                                              name='category_id'
                                              onChange={e => onChange(e)}   //important agregado
                                              value={category.id.toString()}  //important agregado
                                              type='radio'
                                              className='focus:ring-blue-500 h-4 w-4 text-blue-600 border-gray-300 rounded-full'
                                          />
                                          <label className="ml-3 min-w-0 flex-1 text-gray-500">
                                              {category.name}
                                          </label>
                                      </div>
                                  )
                              } else {                                              //SI TIENE SUBCATEGS MUESTRO IGUAL EL PATHER
                                  let result = []
                                  result.push(
                                      <div key={category.id} className='flex items-center h-5'>
                                          <input
                                              name='category_id'
                                              onChange={e => onChange(e)}
                                              value={category.id.toString()}      //SERA EL NUEVO VALOR 
                                              type='radio'
                                              className='focus:ring-blue-500 h-4 w-4 text-blue-600 border-gray-300 rounded-full'
                                          />
                                          <label className="ml-3 min-w-0 flex-1 text-gray-500">
                                              {category.name}
                                          </label>
                                      </div>
                                  )

                                  category.sub_categories.map(sub_category => {
                                      result.push(
                                          <div key={sub_category.id} className='flex items-center h-5 ml-2 my-5'>
                                              <input
                                                  name='category_id'
                                                  onChange={e => onChange(e)}
                                                  value={sub_category.id.toString()}
                                                  type='radio'
                                                  className='focus:ring-blue-500 h-4 w-4 text-blue-600 border-gray-300 rounded-full'
                                              />
                                              <label className="ml-3 min-w-0 flex-1 text-gray-500">
                                                  {sub_category.name}
                                              </label>
                                          </div>
                                      )
                                  })

                                  return result
                              }
                          })
                      }
                    </ul>

                        {/* FILTRO POR PRECIOS-PRICES */}
                    <Disclosure as="div" className="border-t border-gray-200 px-4 py-6">
                    {({ open }) => (
                      <>
                      <h3 className="-mx-2 -my-3 flow-root">
                                  {/* BUTTON PARA DESPLEGAR PANEL DE OPCIONES(Disclosure) */}
                        <Disclosure.Button className="px-2 py-3 bg-white w-full flex items-center justify-between text-gray-400 hover:text-gray-500">
                          <span className="font-sofiapro-regular text-gray-900">Prices</span>
                          <span className="ml-6 flex items-center">
                            {open ? (
                              <MinusSmIcon className="h-5 w-5" aria-hidden="true" />
                            ) : (
                              <PlusSmIcon className="h-5 w-5" aria-hidden="true" />
                            )}
                          </span>
                        </Disclosure.Button>
                                    {/* DESPLIEGUE OPTIONS DE PRECIOS 1 - 19 ETC */}
                        <Disclosure.Panel className="pt-6">
                          <div className="space-y-6">
                            {
                                prices && prices.map((price, index) => {
                                    if (price.id === 0) {              //DE MANERA QUE EL PRIMERO QUE INGRESA SEA ID=0 QUEDA CHEKADO
                                        return (                          
                                            <div key = {index} className='form-check'>
                                                <input
                                                    onChange={e => onChange(e)}
                                                    value={price.name}
                                                    name='price_range'
                                                    type='radio'
                                                    className='focus:ring-blue-500 h-4 w-4 text-blue-600 border-gray-300 rounded-full'
                                                    defaultChecked      //queda checado por default de inicio
                                                />
                                                <label className='ml-3 min-w-0 flex-1 text-gray-500 font-sofiapro-light'>{price.name}</label>
                                            </div>
                                        )
                                    } else {                          //DESP DEL ID=0 PROSIGUE POR AQUI CON LOS SIGUIENTES IDs
                                        return (
                                            <div key={index} className='form-check'>
                                                <input
                                                    onChange={e => onChange(e)}
                                                    value={price.name}
                                                    name='price_range'
                                                    type='radio'
                                                    className='focus:ring-blue-500 h-4 w-4 text-blue-600 border-gray-300 rounded-full'
                                                />
                                                <label className='ml-3 min-w-0 flex-1 text-gray-500 font-sofiapro-light'>{price.name}</label>
                                            </div>
                                        )
                                    }
                                })
                            }
                          </div>
                        </Disclosure.Panel>

                      </h3>
                      </>
                    )}
                    </Disclosure>

                        {/* MAS FILTROS _ POR SELECTION Y ORDER */}
                    <Disclosure as="div" className="border-t border-gray-200 px-4 py-6">
                    {({ open }) => (
                      <>
                      <h3 className="-mx-2 -my-3 flow-root">
                        <Disclosure.Button className="px-2 py-3 bg-white w-full flex items-center justify-between text-gray-400 hover:text-gray-500">
                          <span className="font-sofiapro-regular text-gray-900">Mas Filtros</span>
                          <span className="ml-6 flex items-center">
                            {open ? (
                              <MinusSmIcon className="h-5 w-5" aria-hidden="true" />
                            ) : (
                              <PlusSmIcon className="h-5 w-5" aria-hidden="true" />
                            )}
                          </span>
                        </Disclosure.Button>
                                {/* DESPLIEGUE DEL MENU SELECTION Y ORDER */}
                        <Disclosure.Panel className="pt-6">
                          <div className="space-y-6">
                            <div className='form-group '>
                                <label htmlFor='sortBy' className='mr-3 min-w-0 flex-1 text-gray-500'
                                >Ver por</label>
                                  <select
                                      className='my-2 font-sofiapro-light inline-flex justify-center w-full rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-gray-100 focus:ring-blue-500'
                                      id='sortBy'
                                      name='sortBy'
                                      onChange={e => onChange(e)}
                                      value={sortBy}
                                  >
                                    <option value='date_created'>Fecha</option>
                                    <option value='price'>Precio</option>
                                    <option value='sold'>Sold</option>
                                    <option value='title'>Nombre</option>

                                  </select>
                            </div>
                            <div className='form-group'>
                                <label htmlFor='order' className='mr-3 min-w-0 flex-1 text-gray-500'
                                >Orden</label>
                                <select
                                    className='my-2 font-sofiapro-light inline-flex justify-center w-full rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-gray-100 focus:ring-blue-500'
                                    id='order'
                                    name='order'
                                    onChange={e => onChange(e)}
                                    value={order}
                                >
                                    <option value='asc'>A - Z</option>
                                    <option value='desc'>Z - A</option>
                                </select>
                            </div>
                          </div>
                        </Disclosure.Panel>
                      </h3>
                      </>
                    )}
                    </Disclosure>

                        {/* BUTTON ENVIAR LOS FILTROS-CAMBIOS */}        
                    <button
                      type="submit"
                      className="float-right inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                    >
                      Buscar
                    </button>

                </form>

                {/* Product grid */}
                <div className="lg:col-span-3">
                  {/* Replace with your content */}

                  {products && showProducts()}                    

                </div>
              </div>

            </section>
          </main>

          </div>
        </div>
        </Layout>
    )
}             

const mapStateToProps = state => ({
    categories: state.Categories.categories,
    products: state.Products.products,
    filtered_products: state.Products.filtered_products
})

export default connect(mapStateToProps,{
    get_categories,
    get_products,
    get_filtered_products
}) (Shop)