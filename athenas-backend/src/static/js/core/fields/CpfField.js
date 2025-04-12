/**
 *
 **/
Ext._define('core.fields.CpfField', {
    extend: 'Ext.form.CompositeField',

    setValue: function(value) {
        this.callBackReadNaturalPerson(value);
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
        var finder = /(\s|\.|-)/;

        while(finder.test(value))
            value = value.replace(finder, '');

        return value;
    },

    isNumberCharCode: function(charCode) {
        return (charCode >= 48 && charCode <= 57);
    },

    formatedAppendChar: function(formated, charCode) {
        var valid = false;

        if(formated.length < 14 && this.isNumberCharCode(charCode)) {
            if(formated.length === 3)
                formated += '.';
            else if(formated.length === 7)
                formated += '.';
            else if(formated.length === 11)
                formated += '-';

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

        if(formated.length > 1) {
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
        else if(formated.length === 1) {
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
                // fieldClass: 'x-form-field text-right',
                listeners: {
                    scope: this,
                    change: function(field, value) {
                        this.getHiddenField().setValue(this.clearMask(value));
                        this.keyPressed = false;
                        this.callBackReadNaturalPerson(field.getValue());
                    },
                    keypress: function(field, e) {
                        var value = field.getValue();
                        var stopEvent = true;
                        var rst;

                        if(value.length < 14 && this.isNumberCharCode(e.getCharCode())) {
                            rst = this.formatedAppendChar(value, e.getCharCode());

                            if(rst.valid) {
                                field.setValue(rst.formated);
                                this.keyPressed = true;
                            }
                        }
                        else if(e.getKey() === e.TAB)
                            stopEvent = false;

                        this.callBackReadNaturalPerson(value);

                        if(stopEvent) e.stopEvent();
                    },
                    specialkey: function(field, e) {
                        var key = e.getKey();
                        var rst;


                        if(key === e.BACKSPACE || key === e.DELETE) {
                            rst = this.formatedRemoveLastChar(field.getValue());
                            if(rst.valid) field.setValue(rst.formated);
                            e.stopEvent();
                        }
                        else if(key !== e.TAB) {
                            e.stopEvent();
                        }

                        this.callBackReadNaturalPerson(field.getValue());
                    }
                }
            });

        return this.formatedField;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                validateOnBlur: true,
                callBackReadNaturalPerson: function(){},
            }
        );
        Ext.apply(
            cfg,
            {
                keyPressed: false,
                maxLength: 14,
                items: [
                    this.getFormatedField(cfg),
                    this.getHiddenField(cfg)
                ]
            }
        );
        core.fields.CpfField.superclass.constructor.call(this, cfg);
        this._preventCallBackReadNaturalPerson = false;
    }
});

Ext.reg('cpffield', core.fields.CpfField);
