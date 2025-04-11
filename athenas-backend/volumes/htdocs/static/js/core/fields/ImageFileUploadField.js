
Ext._define('core.fields.ImageFileUploadField', {
    extend: 'core.fields.FileUploadField',

    xtype: 'core-imageuploadfield',

    openWebcamInput: function() {
        Ext._create('core.fields.WebcamInputWindow', {
            crop: (this.crop || false),
            width: (this.captureWidth || 980),
            height: (this.captureHeight || 555),
            cropWidth: (this.cropWidth || false),
            cropHeight: (this.cropHeight || false),
            captureCallback: {
                scope: this,
                fn: function(canvas) {
                    this.uploadURLData(
                        'captured-image.jpg',
                        canvas.toDataURL('image/jpeg', (this.compressRatio || 0.95))
                    );
                }
            }
        }).show();
    },

    _factoryMainButtons: function(cfg) {
        var buttons = [
            {
                xtype: 'button',
                iconCls: 'icon-core icon-core-webcam',
                scope: this,
                handler: function() { this.openWebcamInput(); }
            }
        ];

        buttons = buttons.concat(
            core.fields.ImageFileUploadField.superclass._factoryMainButtons.call(this, cfg)
        );

        return buttons;
    },

    constructor: function(cfg) {
        cfg = (cfg || {});

        Ext.applyIf(cfg, { crop: false });

        core.fields.ImageFileUploadField.superclass.constructor.call(this, cfg)
    }
});
