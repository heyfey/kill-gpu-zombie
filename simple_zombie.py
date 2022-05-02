import tensorflow as tf
import time

make_zombie = True

model = tf.keras.Sequential([
    tf.keras.layers.Conv2D(32, [3, 3], activation='relu'),
    tf.keras.layers.Conv2D(64, [3, 3], activation='relu'),
    tf.keras.layers.MaxPooling2D(pool_size=(2, 2)),
    tf.keras.layers.Dropout(0.25),
    tf.keras.layers.Flatten(),
    tf.keras.layers.Dense(128, activation='relu'),
    tf.keras.layers.Dropout(0.5),
    tf.keras.layers.Dense(10, activation='softmax')
])

model.compile(loss=tf.losses.SparseCategoricalCrossentropy(),
              optimizer=tf.optimizers.Adam(0.01),
              metrics=['accuracy'],
              experimental_run_tf_function=False)

if make_zombie:
    print('sleeping...')
    time.sleep(300)
else:
    (mnist_images, mnist_labels), _ = tf.keras.datasets.mnist.load_data()

    dataset = tf.data.Dataset.from_tensor_slices(
        (tf.cast(mnist_images[..., tf.newaxis] / 255.0,
                 tf.float32), tf.cast(mnist_labels, tf.int64)))

    dataset = dataset.repeat().shuffle(10000).batch(100)

    model.fit(dataset, steps_per_epoch=100000, epochs=1, callbacks=None)
