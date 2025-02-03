function deleteProduct(productId) {
    if (confirm('Are you sure you want to delete this product?')) {
        fetch(`/delete_product/${productId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
        })
        .then(response => {
            if (!response.ok) throw new Error('Failed to delete');
            window.location.reload();
        })
        .catch(error => alert(error.message));
    }
}