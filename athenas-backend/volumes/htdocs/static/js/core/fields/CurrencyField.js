/**
 *
 **/
Ext._define('core.fields.CurrencyField', {
    extend: 'Ext.form.CompositeField',

    keyPressed: false,

    setValue: function(value) {

        this.getHiddenField().setValue(value);

        value = this.validateInitialValue(value);

        this.getFormatedField().setValue(this.addMask(value));

    },

    /**
    * verifica, através de expressão regular, se o valor é composto de apenas dígitos, sinal negativo '-',
    * e ponto '.' decimal. Se não satisfazer a expressão, é retornado uma string vazia.
    */
    validateInitialValue: function(value) {
        var finder = /(^-?(\d+)(\.)?(\d+)?$)/;
        value = value.toString();
        var validValue = "";

        if(finder.test(value)){
            validValue = value;
        }

        validValue = this.decimalInitialValue(validValue);

        return validValue;
    },

    /**
    * valor de casa decimal separado por ponto '.'.
    * se o valor passado por parâmetro não possue casa decimal, é adicionado uma.
    * se o valor possua casa decimal, e essa casa for de apenas um dígito. adiciona-se um '0' a casa decimal.
    * Caso o valor possua casa decimal maior que dois dígitos, conserva-se apenas os dois iniciais.
    */
    decimalInitialValue: function(value) {
        var finder = /(\.)/;

        if(value.length > 0) {
            if(finder.test(value)) {
                var parts = value.split('.');

                if(parts[1].length > 2)
                    parts[1] = parts[1].substr(0, 2);
                else if(parts[1].length === 1)
                    parts[1] += '0';

                value = parts.join();

            } else {
                value += '.00';
            }
        }

        return value;
    },

    getHiddenField: function(cfg) {
        if(!this._hiddenField)
            this._hiddenField = Ext._create('Ext.form.Hidden', cfg);

        return this._hiddenField;
    },

    /**
    * limpa a mascara
    *
    */
    clearMask: function(value) {
        var finder = /(\s|\,|\.)/;
        while(finder.test(value))
            value = value.replace(finder, '');

        return this.removeSignal(value);
    },

    /*
    * remove sinal '-'. Utilizado para impedir que seja inserido apenas o sinal no campo
    */
    removeSignal: function(value) {
        return value.replace(/^\-$/, '');
    },


    isZero: function(value) {
        var finder = /(^-?0\,00$)/;
        var zero = true ? (value.search(finder) === 0 || value.length === 0) : false;
        return zero;
    },

    /**
    * remove os zeros a esquerda.
    */
    clearZero: function(value) {
        var finder = /(^-?[0]+)/;
        var signal = '';
        if(this.isNumberNegative(value)){
            value = value.split('-')[1];
            signal = '-';
        }

        value = value.replace(finder,'');
        finder = /(^[\,])/;
        value = value.replace(finder,'0$1');
        return signal+value;
    },


    isNumberCharCode: function(charCode) {
        return (charCode >= 48 && charCode <= 57);
    },

    isNegativeCharCode: function(charCode) {
        return charCode === 45;
    },

    isNumberNegative: function(formated) {
        var finder = /(^[\-])/;
        return true ? formated.search(finder) === 0: false;
    },

    formatedAppendChar: function(formated, charCode) {
        var valid = false;

        if(this.isNumberCharCode(charCode)){
            if(formated.length === 0)
                formated = "00";
            else if(formated.length === 1 && this.isNumberNegative(formated))
                formated += "00";

            formated += String.fromCharCode(charCode);

            formated = this.addMask(formated);

            if(this.isNumberNegative(formated) && this.isZero(formated))
                formated = "";

            valid = true;
        } else if(this.isNegativeCharCode(charCode)) {
            if(formated.length === 0){
                formated = '-';
                valid = true;
            }
        }

        return {
            valid: valid,
            formated: formated
        };
    },

    addMask: function(value) {
        value = this.clearMask(value);
        value = this.formateMilhar(this.formateDecimal(value));
        return this.clearZero(value);
    },

    formateDecimal: function(value, separator){
        var finder = /(\d)(\d{2}$)/;
        separator = core.nullValue(separator, ",");

        while(finder.test(value))
            value = value.replace(finder, '$1'+separator+'$2');
        return value;
    },

    formateMilhar: function(value){
        var finder = /(\d+)(\d{3})/;
        while(finder.test(value))
            value = value.replace(finder, '$1' + '.' + '$2');
        return value;
    },


    formatedRemoveLastChar: function(formated) {
        var valid = false;
        var rst;

        if(!this.isZero(formated)) {

            formated = this.clearMask(formated);

            if(this.isNumberNegative(formated) && formated.length === 4)
                formated = "-0" + formated.split('-')[1];
            else if(formated.length === 3)
                formated = "0" + formated;

            var last = formated.substr((formated.length - 2), 1);

            rst = this.formatedAppendChar(formated.substr(0, formated.length - 2 ), last.charCodeAt(0));

        } else {
            rst = {
                valid: true,
                formated: ""
            };
        }

        return {
            valid: rst.valid,
            formated: rst.formated
        };
    },

    /**
    * Retorna o valor sem mascara e com casa decimal.
    */
    getValueWithPointFloating: function(value){
        return this.formateDecimal(this.clearMask(value), '.');
    },

    getFormatedField: function(cfg) {
        if(!this.formatedField)
            this.formatedField = Ext._create('Ext.form.TextField', {
                allowBlank: cfg.allowBlank,
                submitValue: false,
                enableKeyEvents: true,
                width: (cfg.width || 100) - 1,
                tabIndex: cfg.tabIndex,
                fieldClass: 'x-form-field text-right',
                listeners: {
                    scope: this,
                    change: function(field, value) {
                        if(this.keyPressed) {

                            field.setValue(this.removeSignal(value));

                            this.getHiddenField().setValue(this.getValueWithPointFloating(value));
                            this.keyPressed = false;
                        }
                    },
                    keypress: function(field, e) {
                        var value = field.getValue();
                        var stopEvent = true;
                        var rst;

                        if(value.length < 20 && (this.isNumberCharCode(e.getCharCode()) || this.isNegativeCharCode(e.getCharCode()))) {
                            rst = this.formatedAppendChar(value, e.getCharCode());

                            if(rst.valid) {
                                field.setValue(rst.formated);
                                this.keyPressed = true;
                            }
                        } else if(e.getKey() === e.TAB)
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

        core.fields.CurrencyField.superclass.constructor.call(this, cfg);
    }
});

Ext.reg('currencyfield', core.fields.CurrencyField);
