import React from "react";

import ResourcePage from "../components/ResourcePage";
import "./Products.css";

const PRODUCT_COLUMNS = [
    {
        key: "sku",
        label: "SKU",
    },
    {
        key: "name",
        label: "Product",
    },
    {
        key: "category",
        label: "Category",
    },
    {
        key: "brand",
        label: "Brand",
    },
];

const PRODUCT_FIELDS = [
    {
        key: "sku",
        label: "SKU",
    },
    {
        key: "name",
        label: "Product name",
    },
    {
        key: "category",
        label: "Category",
        required: false,
    },
    {
        key: "brand",
        label: "Brand",
        required: false,
    },
];

const normalizeProduct = (formData) => ({
    sku: formData?.sku?.trim() || "",
    name: formData?.name?.trim() || "",
    category: formData?.category?.trim() || "",
    brand: formData?.brand?.trim() || "",
});

export default function Products() {
    return (
        <ResourcePage
            resource="products"
            title="Products"
            description="Maintain the product catalogue used by attention scoring and shelf mapping."
            columns={PRODUCT_COLUMNS}
            fields={PRODUCT_FIELDS}
            normalize={normalizeProduct}
        />
    );
}