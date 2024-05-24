from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from posts.models import Post
from .forms import PostForm
from django.http import FileResponse
from reportlab.pdfgen import canvas

def generate_pdf(request):
    response = FileResponse(generate_pdf_file(), 
                            as_attachment=True, 
                            filename='book_catalog.pdf')
    return response
 
 
def generate_pdf_file():
    from io import BytesIO
 
    buffer = BytesIO()
    p = canvas.Canvas(buffer)
 
    # Create a PDF document
    books = Post.objects.all()
    p.drawString(100, 750, "News Catalog")
 
    y = 700
    for book in books:
        p.drawString(100, y, f"Title: {book.title}")
        p.drawString(100, y - 20, f"Content: {book.content}")
        p.drawString(100, y - 40, f"Author: {book.created_by}")
        y -= 60
 
    p.showPage()
    p.save()
 
    buffer.seek(0)
    return buffer


def index_view(request):
    posts = Post.objects.all()
    context = {
        'posts': posts,
    }
    return render(request, 'posts/index.html', context)


def post_detail_view(request, pk):
    post = Post.objects.get(pk=pk)
    context = {
        'post': post,
    }
    return render(request, 'posts/detail.html', context)


@login_required
def post_create_view(request):
    form = PostForm(request.POST, request.FILES)
    if form.is_valid():
        form.save(commit=False)
        form.instance.created_by = request.user
        form.save()
        return redirect('index')
    return render(request, 'posts/create_form.html', {'form': form})


@login_required
def post_update_view(request, pk):
    post = get_object_or_404(Post, pk=pk, created_by=request.user)
    form = PostForm(request.POST or None, request.FILES or None, instance=post)
    if form.is_valid():
        form.save()
        return redirect('index')
    return render(request, 'posts/update_form.html', {'form': form})


def post_delete_view(request, pk):
    post = get_object_or_404(Post, pk=pk, created_by=request.user)
    if request.method == 'POST':
        post.delete()
        return redirect('index')
    return render(request, 'posts/delete_form.html', {'post': post})
