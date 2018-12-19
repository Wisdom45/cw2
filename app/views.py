from app import app,db
from datetime import datetime
from flask import render_template, flash, redirect, request, session, url_for
from flask_login import login_user, logout_user, login_required, current_user
from .models import User, Role, Permission, Post, Comment
from .forms import LoginForm, RegistrationForm, PostForm, CommentForm, ChangePasswordForm, EditProfileForm

@app.route('/', methods=['GET', 'POST'])
def index():
    posts = Post.query.order_by(Post.timestamp.desc()).all()
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            info = '%s login the blog.'%(user.username)
            app.logger.info(info)
            next = request.args.get('next')
            if next is None or not next.startswith('/'):
                next = '/'
            return redirect(next)
        flash('Invalid username or password.')
    return render_template('index.html', posts=posts,form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            info = '%s login the blog.'%(user.username)
            app.logger.info(info)
            next = request.args.get('next')
            if next is None or not next.startswith('/'):
                next = '/'
            return redirect(next)
        flash('Invalid username or password.')
        app.logger.info('login success')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    info = '%s leave the blog.'%(current_user.username)
    app.logger.info(info)
    logout_user()
    flash('You have been logged out.')
    return redirect('/')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data, username=form.username.data,
                    password=form.password.data, role_id=1)
        db.session.add(user)
        db.session.commit()
        info = '%s register an account.'%(user.username)
        app.logger.info(info)
        flash('You can now login.')
        return redirect("/login")
    return render_template("register.html", form=form)

@app.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password.data
            db.session.add(current_user)
            db.session.commit()
            info = '%s change his password.'%(current_user.username)
            app.logger.info(info)
            flash('Your password has been updated.')
            return redirect('/')
        else:
            warn = '%s enter a wrong old password.'%(current_user.username)
            app.logger.warn(warn)
            flash('The old password you enter is wrong.')
    return render_template("change_password.html", form=form)

@app.route('/profile/<id>')
def profile(id):
    user = User.query.filter_by(id=id).first()
    info = 'The profile of %s is read by someone.'%(user.username)
    app.logger.info(info)
    return render_template('profile.html', user=user)

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        current_user.member_since = datetime.utcnow()
        db.session.add(current_user._get_current_object())
        db.session.commit()
        info = 'The profile of %s is changed.'%(current_user.username)
        app.logger.info(info)
        flash('Your profile has been updated.')
        return redirect(url_for('.profile', id=current_user.id))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)

@app.route('/manage_user',methods=['GET', 'POST'])
@login_required
def manage_user():
    users = User.query.filter_by(role_id=1 or 2).all()
    return render_template('manage_user.html', users = users)

@app.route('/delete_user/<id>',methods=['GET','POST'])
def delete_user(id):
    if current_user.can(Permission.ADMINISTER):
        user = User.query.get(id)
        db.session.delete(user)
        db.session.commit()
        warn = 'The account of %s is deleted.'%(user.username)
        app.logger.warn(warn)
        return redirect(url_for('.manage_user'))
    else:
        error = 'Error, the %s has no permission.'%(curent_user.username)
        app.logger.error(error)
        redirect('/')



@app.route('/write_blog',methods=['GET', 'POST'])
def write_blog():
    form = PostForm()
    if current_user.can(Permission.WRITE_ARTICLES) and form.validate_on_submit():
        post = Post(title=form.title.data, body=form.body.data, author=current_user._get_current_object())
        db.session.add(post)
        db.session.commit()
        info = '%s write a new blog.'%(current_user.username)
        app.logger.info(info)
        return redirect('/')
    return render_template('write_blog.html', form=form)

@app.route('/comment/<id>',methods=['GET', 'POST'])
def comment(id):
    comments = Comment.query.filter_by(post_id=id).order_by(Comment.timestamp.desc()).all()
    post = Post.query.get(id)
    info = 'The  "%s" of %s is read by someone.'%(post.title,post.author.username)
    app.logger.info(info)
    form = CommentForm()
    id = post.id
    if  form.validate_on_submit():
        comment = Comment(content = form.comment.data, author=current_user._get_current_object(), post=post)
        if current_user.can(Permission.COMMENT):
            info = 'The %s write a comment for the post "%s" of %s.'%(curent_user.username,post.title,post.author.username)
            app.logger.info(info)
        else:
            error = 'Error, the %s has no permission.'%(curent_user.username)
            app.logger.error(error)
        db.session.add(comment)
        db.session.commit()
        flash('Your comment has been published.')
        return redirect(url_for('.comment',id = id))
    return render_template('post.html', form=form, comments = comments, post = post)


@app.route('/delete_comment/<id>', methods=['GET','POST'])
def delete_comment(id):
    comment = Comment.query.get(id)
    id = comment.post_id
    if current_user.can(Permission.MODERATE_COMMENTS):
        warn = 'The comement whose id is %s of %s is deleted.'%(comment.id,comment.author.username)
        app.logger.warn(warn)
    else:
        error = 'Error, the %s has no permission.'%(curent_user.username)
        app.logger.error(error)
    db.session.delete(comment)
    db.session.commit()
    return redirect(url_for('.comment',id = id))

@app.route('/my_blog/<id>',methods=['GET','POST'])
def manage_blog(id):
    posts = Post.query.filter_by(author_id = id).order_by(Post.timestamp.desc()).all()
    return render_template('manage_blog.html',posts = posts)

@app.route('/delete_post/<id>',methods=['GET','POST'])
def delete_post(id):
    post = Post.query.get(id)
    warn = 'The post "%s" of %s is deleted.'%(post.title,post.author.username)
    app.logger.warn(warn)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('.manage_blog',id = current_user.id))

@app.route('/edit_post/<id>',methods=['GET','POST'])
def edit_post(id):
    post = Post.query.get(id)
    form = PostForm(obj=post)
    if form.validate_on_submit():
        p = post
        p.title =form.title.data
        p.body=form.body.data
        db.session.commit()
        warn = 'The post "%s" of %s is changed.'(post.title,post.author.username)
        app.logger.warn(warn)
        return redirect(url_for('.manage_blog',id = current_user.id))
    return render_template('edit_blog.html', form=form)

@app.route('/follow/<id>')
@login_required
def follow(id):
    user = User.query.filter_by(id=id).first()
    if user is None:
        flash('Invalid user.')
        return redirect('/')
    if current_user.is_following(user):
        flash('You are already following this user.')
        return redirect(url_for('.profile', id=id))
    current_user.follow(user)
    info = 'The %s follow the %s.'(current_user.username,user.username)
    app.logger.info(info)
    db.session.commit()
    flash('You are now following %s.' % user.username)
    return redirect(url_for('.profile', id=id))


@app.route('/unfollow/<id>')
@login_required
def unfollow(id):
    user = User.query.filter_by(id=id).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    if not current_user.is_following(user):
        flash('You are not following this user.')
        return redirect(url_for('.profile', id=id))
    current_user.unfollow(user)
    info = 'The %s unfollow the %s.'(current_user.username,user.username)
    app.logger.info(info)
    db.session.commit()
    flash('You are not following %s anymore.' % user.username)
    return redirect(url_for('.profile', id=id))

@app.route('/follower_blog',methods=['GET','POST'])
def follower_blog():
    posts = current_user.followed_posts
    return render_template('follower_blog.html', posts=posts)
