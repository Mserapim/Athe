/**
 *
 */

Ext.ns('toolkit.fields');

toolkit.fields.DateTimeField = Ext.extend(
    Ext.form.TextField,
    {
        constructor: function(cfg) {
            cfg = (cfg ? cfg : {});
            Ext.applyIf(cfg, {
                'dateFormat': Ext.form.DateField.prototype.format,
                'timeFormat': 'H:i',
                'separator': ' '
            });

            toolkit.fields.DateTimeField.superclass.constructor.call(this, cfg);

            if(this.value) this.setValue(this.value);
        },

        _getDateObjectFormat: function() {
            return this.dateFormat + this.separator + this.timeFormat;
        },

        setValue: function(newValue) {
            if(!(newValue instanceof Date))
                newValue = Date.parseDate(newValue, this._getDateObjectFormat());

            if(newValue) {
                toolkit.fields.DateTimeField.superclass.setValue.call(this, newValue.format(this._getDateObjectFormat()));

                var value = this._valueToObject();
                this.getDateField().setValue(value.date);
                this.getTimeField().setValue(value.time);
            }
        },

        _valueToObject: function(value) {
            var dt = this.getValue();

            return {
                'date': dt.format(this.dateFormat),
                'time': dt.format(this.timeFormat),
                'separator': this.separator,

                'toString': function() {
                    return this.date + this.separator + this.time;
                }
            }
        },

        getValue: function() {
            var value = toolkit.fields.DateTimeField.superclass.getValue.call(this);

            return Date.parseDate(value, this._getDateObjectFormat());
        },

        getDateField: function() {
            if(!this._datefield)
                this._datefield = new Ext.form.DateField({
                    'width': 100,
                    'submitValue': false,
                    'allowBlank': this.allowBlank,
                    'listeners': {
                        'scope': this,
                        'change': function(field, newValue, oldValue) { this._doValue() }
                    }
                });

            return this._datefield;
        },

        _doValue: function() {
            this.setValue(this.getDateField().getValue().format('d/m/Y') + ' ' + this.getTimeField().getValue());
        },

        getTimeField: function() {
            if(!this._timeField)
                this._timeField = new Ext.form.TextField({
                    'width': 60,
                    'enableKeyEvents': true,
                    'submitValue': false,
                    'allowBlank': this.allowBlank,
                    'validator': function(value) {
                        var tests = [
                            /^$/,
                            /^[0-2]$/,
                            /^([0-1][0-9]|2[0-3])$/,
                            /^([0-1][0-9]|2[0-3]):$/,
                            /^([0-1][0-9]|2[0-3]):[0-5]$/,
                            /^([0-1][0-9]|2[0-3]):[0-5][0-9]$/,
                        ];

                        var flag = false;
                        Ext.each(tests, function(t) {
                            if(t.test(value)) {
                                flag = true;
                                return false;
                            }
                        });

                        return (flag ? true : 'Horário informado é inválido.');
                    },
                    'listeners': {
                        'scope': this,
                        'keypress': function(field, evt) {
                            if(evt.charCode >= 48 && evt.charCode <= 57) {
                                var value = field.getValue();
                                if(value.length == 2)
                                    field.setValue(value + ':')
                                else if(value.length == 5)
                                    evt.stopEvent()
                            }
                            else if(evt.charCode != 0){
                                evt.stopEvent();
                                //console.debug([evt, evt.charCode, evt.keyCode]);
                            }
                        },
                        change: function(field, newValue, oldValue) { this._doValue(); }
                    }
                });

            return this._timeField;
        },

        onRender: function(container, position) {
            var p1 = new Ext.Panel({
                'items': this.getDateField(),
                'border': false
            });

            var p2 = new Ext.Panel({
                'items': this.getTimeField(),
                'border': false,
                'margins': '0 0 0 5'
            });

            var p3 = new Ext.Panel({
                'width': 0
            });

            var pn = new Ext.Panel({
                'layout': 'hbox',
                'renderTo': container,
                'items': [p1, p2, p3],
                'border': false,
                'width': 200
            });

            this.inputType = 'hidden'
            toolkit.fields.DateTimeField.superclass.onRender.call(this, p3.body);
        }
    }
);

toolkit.fields.DateTimeExtendedField = Ext.extend(
    toolkit.fields.DateTimeField,
    {
        _getDateObjectFormat: function() {
            var _format = '';
            if(this.getDateField())
                _format = this.dateFormat + this.separator;
            _format = _format + this.timeFormat;
            return _format;
        },

        setValue: function(newValue) {
            if(!(newValue instanceof Date)){
                if(this.getDateField())
                    newValue = Date.parseDate(newValue, this._getDateObjectFormat());
            }
            if(newValue) {
                if(this.getDateField())
                    toolkit.fields.DateTimeField.superclass.setValue.call(this, newValue.format(this._getDateObjectFormat()));
                else{
                    if(newValue.indexOf(':') == -1)
                        newValue = newValue.slice(0, 2) + ':' + newValue.slice(2, 4);
                    toolkit.fields.DateTimeField.superclass.setValue.call(this, newValue);
                }

                var value = this._valueToObject();
                if(this.getDateField())
                    this.getDateField().setValue(value.date);
                this.getTimeField().setValue(value.time);
            }
        },

        _valueToObject: function(value) {
            var dt = this.getValue();
            return {
                date: this.getDateField() ? dt.format(this.dateFormat) : '',
                time: this.getDateField() ? dt.format(this.timeFormat) : dt,
                separator: this.separator,
                toString: function() {
                    var value = '';
                    if(this.date != '')
                        value = this.date + this.separator;
                    value = value + this.time;
                    return value;
                }
            }
        },

        getValue: function() {
            var value = toolkit.fields.DateTimeField.superclass.getValue.call(this);
            var dt = value;
            if(this.getDateField())
                dt = Date.parseDate(value, this._getDateObjectFormat());
            return dt;
        },

        getDateField: function() {
            return undefined;
        },

        _doValue: function() {
            if(this.getDateField())
                this.setValue(this.getDateField().getValue().format('d/m/Y') + ' ' + this.getTimeField().getValue());
            else
                this.setValue(this.getTimeField().getValue());
        },

        getTimeField: function() {
            if(!this._timeField)
                this._timeField = new Ext.form.TextField({
                    width: 60,
                    enableKeyEvents: true,
                    submitValue: false,
                    allowBlank: this.allowBlank,
                    validator: function(value) {
                        var tests = [
                            /^$/,
                            /^[0-2]$/,
                            /^([0-1][0-9]|2[0-3])$/,
                            /^([0-1][0-9]|2[0-3]):$/,
                            /^([0-1][0-9]|2[0-3]):[0-5]$/,
                            /^([0-1][0-9]|2[0-3]):[0-5][0-9]$/,
                        ];

                        var flag = false;
                        Ext.each(tests, function(t) {
                            if(t.test(value)) {
                                flag = true;
                                return false;
                            }
                        });

                        return (flag ? true : 'Horário informado é inválido.');
                    },
                    listeners: {
                        scope: this,
                        keyup: function(field, evt) {
                            var el = field.getEl();
                            var selectionStart = el.dom.selectionStart;
                            var selectionEnd = el.dom.selectionEnd;
                            var oldValue = field.getValue();

                            valueDigits = oldValue.replace(':', '');
                            if(oldValue.length == 2 && !/\D/.test(oldValue)){
                                var newValue = oldValue + ':';
                                field.setValue(newValue);
                                field.fireEvent('change', [field, newValue, oldValue]);
                            }else if(valueDigits.length > 4 && !/\D/.test(valueDigits)){
                                var newValue = valueDigits.slice(0, 2) + ':' + valueDigits.slice(2, valueDigits.length -1);
                                field.setValue(newValue);
                                field.fireEvent('change', [field, newValue, oldValue]);
                            }

                            if(oldValue.length >=5){
                                if(selectionStart == 3){
                                    selectionStart = 4;
                                    selectionEnd = 4;
                                }
                                if(!this._prevent){
                                    el.dom.selectionStart = selectionStart;
                                    el.dom.selectionEnd = selectionEnd;
                                }
                            }
                        },
                        keypress: function(field, evt) {
                            if(evt.charCode >= 48 && evt.charCode <= 57)
                                this._prevent = false;
                            else{
                                this._prevent = true;
                                evt.stopEvent();
                            }
                        },
                        change: function(field, newValue, oldValue) {this._doValue(); }
                    }
                });

            return this._timeField;
        }
    }
);

Ext.reg('tk-datetimefield', toolkit.fields.DateTimeField);
Ext.reg('tk-datetimeextendedfield', toolkit.fields.DateTimeExtendedField);