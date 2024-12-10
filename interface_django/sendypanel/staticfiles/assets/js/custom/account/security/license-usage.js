"use strict";
var KTAccountSecurityLicenseUsage = {
    init: function () {
        KTUtil.each(document.querySelectorAll('#kt_security_license_usage_table [data-action="copy"]'), (function (e) {
            var t = e.closest("tr"),
                c = KTUtil.find(t, '[data-bs-target="license"]');
            new ClipboardJS(e, {
                target: c,
                text: function () {
                    return c.innerHTML
                }
            }).on("success", (function (t) {
                var s = e.querySelector(".ki-copy"),
                    i = e.querySelector(".ki-check");
                i || ((i = document.createElement("i")).classList.add("ki-solid"), i.classList.add("ki-check"), i.classList.add("fs-2"), e.appendChild(i), c.classList.add("text-success"), s.classList.add("d-none"), setTimeout((function () {
                    s.classList.remove("d-none"), e.removeChild(i), c.classList.remove("text-success")
                }), 3e3))
            }))
        }))
    }
};
KTUtil.onDOMContentLoaded((function () {
    KTAccountSecurityLicenseUsage.init()
}));