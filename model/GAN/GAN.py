from model.AbstractGANModel import AbstractGANModel
from util.Stacker import Stacker
from util.tensor_ops import *
from util.summary_func import summary_loss
from dict_keys.dataset_batch_keys import *
import numpy as np
import tensorflow as tf


class GAN(AbstractGANModel):
    VERSION = 1.0
    AUTHOR = 'demetoir'

    def __str__(self):
        return "%s_%s_%f" % (self.AUTHOR, self.__class__.__name__, self.VERSION)

    def load_hyper_parameter(self):
        self.n_noise = 256
        self.batch_size = 64
        self.learning_rate = 0.0002

    def generator(self, z, reuse=False):
        with tf.variable_scope('generator', reuse=reuse):
            layer = Stacker(z)
            layer.add_layer(linear, 4 * 4 * 512)
            layer.add_layer(tf.reshape, [self.batch_size, 4, 4, 512])

            layer.add_layer(conv2d_transpose, [self.batch_size, 8, 8, 256], CONV_FILTER_5522)
            layer.add_layer(bn)
            layer.add_layer(relu)

            layer.add_layer(conv2d_transpose, [self.batch_size, 16, 16, 128], CONV_FILTER_5522)
            layer.add_layer(bn)
            layer.add_layer(relu)

            layer.add_layer(conv2d_transpose, [self.batch_size, 32, 32, 3], CONV_FILTER_5522)

            layer.add_layer(conv2d, self.input_c, CONV_FILTER_3311)
            layer.add_layer(tf.sigmoid)
            net = layer.last_layer

        return net

    def discriminator(self, x, reuse=None):
        with tf.variable_scope('discriminator', reuse=reuse):
            layer = Stacker(x)
            layer.add_layer(conv2d, 64, CONV_FILTER_5522)
            layer.add_layer(bn)
            layer.add_layer(lrelu)

            layer.add_layer(conv2d, 128, CONV_FILTER_5522)
            layer.add_layer(bn)
            layer.add_layer(lrelu)

            layer.add_layer(conv2d, 256, CONV_FILTER_5522)
            layer.add_layer(bn)
            layer.add_layer(lrelu)

            layer.add_layer(tf.reshape, [self.batch_size, -1])
            out_logit = layer.add_layer(linear, 1)
            out = layer.add_layer(tf.sigmoid)

        return out, out_logit

    def load_main_tensor_graph(self):
        self.X = tf.placeholder(tf.float32, [self.batch_size] + self.shape_data_x)
        self.z = tf.placeholder(tf.float32, [self.batch_size, self.n_noise])

        self.G = self.generator(self.z)
        self.D_real, self.D_real_logit = self.discriminator(self.X)
        self.D_gen, self.D_gene_logit = self.discriminator(self.G, True)

    def load_loss_function(self):
        with tf.variable_scope('loss'):
            with tf.variable_scope('loss_D_real'):
                self.loss_D_real = tf.reduce_mean(self.D_real)

            with tf.variable_scope('loss_D_gen'):
                self.loss_D_gen = tf.reduce_mean(self.D_gen)

            with tf.variable_scope('loss_D'):
                self.loss_D = - tf.reduce_mean(tf.log(self.D_real)) - tf.reduce_mean(tf.log(1. - self.D_gen))

            with tf.variable_scope('loss_G'):
                self.loss_G = - tf.reduce_mean(tf.log(self.D_gen))

    def loss_alternative(self):
        self.loss_D_real = tf.reduce_mean(
            tf.nn.sigmoid_cross_entropy_with_logits(
                logits=self.D_real_logit, labels=tf.ones_like(self.D_real)))
        self.loss_D_gen = tf.reduce_mean(
            tf.nn.sigmoid_cross_entropy_with_logits(
                logits=self.D_gene_logit, labels=tf.zeros_like(self.D_gen)))
        self.loss_D = self.loss_D_real + self.loss_D_gen

        self.loss_G = tf.reduce_mean(
            tf.nn.sigmoid_cross_entropy_with_logits(
                logits=self.D_gene_logit, labels=tf.ones_like(self.D_gen)))

    def load_train_ops(self):
        self.vars_D = tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES,
                                        scope='discriminator')
        self.train_D = tf.train.AdamOptimizer(learning_rate=self.learning_rate) \
            .minimize(self.loss_D, var_list=self.vars_D)

        self.vars_G = tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES,
                                        scope='generator')
        self.train_G = tf.train.AdamOptimizer(learning_rate=self.learning_rate) \
            .minimize(self.loss_G, var_list=self.vars_G)

    def load_misc_ops(self):
        super().load_misc_ops()

    def train_model(self, sess=None, iter_num=None, dataset=None):
        noise = self.get_noise()
        batch_xs = dataset.next_batch(self.batch_size, batch_keys=[BATCH_KEY_TRAIN_X])
        sess.run(self.train_G, feed_dict={self.z: noise})
        sess.run(self.train_D, feed_dict={self.X: batch_xs, self.z: noise})
        sess.run([self.op_inc_global_step])

    def get_noise(self):
        return np.random.uniform(-1.0, 1.0, size=[self.batch_size, self.n_noise])

    def load_summary_ops(self):
        summary_loss(self.loss_D_gen)
        summary_loss(self.loss_D_real)
        summary_loss(self.loss_D)
        summary_loss(self.loss_G)

        self.op_merge_summary = tf.summary.merge_all()

    def write_summary(self, sess=None, iter_num=None, dataset=None, summary_writer=None):
        noise = self.get_noise()
        batch_xs = dataset.next_batch(self.batch_size, batch_keys=[BATCH_KEY_TRAIN_X])
        summary, global_step = sess.run([self.op_merge_summary, self.global_step],
                                        feed_dict={self.X: batch_xs, self.z: noise})
        summary_writer.add_summary(summary, global_step)
