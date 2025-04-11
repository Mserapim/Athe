
Ext._define('judicial.PartLawsuitMixin', {

    createLoadMask: function() {
      return {
        show: Ext.emptyFn,
        hide: Ext.emptyFn,
      }
    },

    signSuccessCallback: function() {
        console.log('abstract method signSuccessCallback');
    },

    signFailureCallback: function(message) {
        console.log('abstract method signFailureCallback');
    },

    save: core.RestfulWindow.prototype.save,

    factoryRestful: core.RestfulWindow.prototype.factoryRestful,

    _prepareSuccessCallback: function(cb, close) { return cb; },

    getFormPanel: function() {
        return {
            getForm: function() {
                return {
                    getValues: function() {
                        return {}
                    }
                };
            }
        };
    },

    _sign: function() {
        var rest = this.factoryRestful();
        var mask = this.createLoadMask();

        mask.show();
        rest.doRequest(
            rest.getRoute('sign', this.oId, 'PUT', {
                scope: this,
                callback: function() {
                    mask.hide();
                },
                success: function(xhr) {
                    rst = Ext.decode(xhr.responseText);

                    if(rst.success)
                        this.signSuccessCallback();
                    else
                        this.signFailureCallback(rst.message);
                },
                failure: function() {
                    this.signFailureCallback('O sistema esta indisponível neste momento.');
                }
            })
        );
    }
});
