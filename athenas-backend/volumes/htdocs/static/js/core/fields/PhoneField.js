/**
 *
 **/
Ext._define('core.fields.PhoneField', {
    extend: 'Ext.form.CompositeField',

    keyPressed: false,

    setValue: function(value) {
        this.getHiddenField().setValue(value);

        if(!this.keyPressed) {
            var formatedValue = '';

            for(var c = 0; c < value.length; c++)
                formatedValue = this.formatedAppendChar(formatedValue, value.charCodeAt(c)).formated;

            this.getFormatedField().setValue(formatedValue);
        }
    },

    getHiddenField: function(cfg) {
        if(!this._hiddenField)
            this._hiddenField = Ext._create('Ext.form.Hidden', cfg);

        return this._hiddenField;
    },

    clearMask: function(value) {
        var finder = /(\s|\)|\(|-)/;

        while(finder.test(value))
            value = value.replace(finder, '');

        return value;
    },

    isNumberCharCode: function(charCode) {
        return (charCode >= 48 && charCode <= 57);
    },

    formatedAppendChar: function(formated, charCode) {
        var valid = false;

        if(formated.length < 15 && this.isNumberCharCode(charCode)) {
            if(formated.length === 0)
                formated += '(';
            else if(formated.length === 3)
                formated += ') ';
            else if(formated.length === 9)
                formated += '-';
            else if(formated.length === 14) {
                var parts = formated.split('-');

                parts[0] += parts[1].charAt(0);
                parts[1] = parts[1].substr(1);

                formated = parts.join('-');
            }

            formated += String.fromCharCode(charCode);
            valid = true;
        }

        return {
            valid: valid,
            formated: formated
        };
    },

    formatedRemoveLastChar: function(formated) {
        var valid = false;
        var rst;

        if(formated.length > 2) {
            var lastChar = formated.substr((formated.length - 2), 1);

            if(this.isNumberCharCode(lastChar.charCodeAt(0))) {
                rst = this.formatedAppendChar(
                    formated.substr(0, (formated.length - 2)),
                    lastChar.charCodeAt(0)
                );
            }
            else
                rst = this.formatedRemoveLastChar(formated.substr(0, (formated.length - 1)));

            formated = rst.formated;
            valid = rst.valid;
        }
        else if(formated.length === 2) {
            valid = true;
            formated = '';
        }

        return {
            valid: valid,
            formated: formated
        };
    },

    getFormatedField: function(cfg) {
        if(!this.formatedField)
            this.formatedField = Ext._create('Ext.form.TextField', {
                allowBlank: cfg.allowBlank,
                submitValue: false,
                enableKeyEvents: true,
                width: (cfg.width || 100),
                fieldClass: 'x-form-field text-right',
                listeners: {
                    scope: this,
                    change: function(field, value) {
                        if(this.keyPressed) {
                            this.getHiddenField().setValue(this.clearMask(value));
                            this.keyPressed = false;
                        }
                    },
                    keypress: function(field, e) {
                        var value = field.getValue();
                        var stopEvent = true;
                        var rst;

                        if(value.length < 15 && this.isNumberCharCode(e.getCharCode())) {
                            rst = this.formatedAppendChar(value, e.getCharCode());

                            if(rst.valid) {
                                field.setValue(rst.formated);
                                this.keyPressed = true;
                            }
                        }
                        else if(e.getKey() === e.TAB)
                            stopEvent = false;

                        if(stopEvent) e.stopEvent();
                    },
                    specialkey: function(field, e) {
                        var key = e.getKey();
                        var rst;

                        if(key === e.BACKSPACE || key === e.DELETE) {
                            rst = this.formatedRemoveLastChar(field.getValue());
                            if(rst.valid){
                                field.setValue(rst.formated);
                                this.keyPressed = true;
                            }
                            e.stopEvent();
                        }
                        else if(key !== e.TAB) {
                            e.stopEvent();
                        }
                    }
                }
            });

        return this.formatedField;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.apply(
            cfg,
            {
                layout: 'vbox',
                items: [
                    this.getFormatedField(cfg),
                    this.getHiddenField(cfg)
                ]
            }
        );

        core.fields.PhoneField.superclass.constructor.call(this, cfg);
    }
});

Ext.reg('fonefield', core.fields.PhoneField);
